#!/usr/bin/env python
# -*- coding:utf-8 -*-
#===============================================================================
#     File: $Name: RSL.py $
# Revision: $Rev: 1db8652a $
#  Created: $Date: 2013-08-26 22:53:24 $
# Modified: $Date: 2014-06-18 09:30:03 $
#   Author: $Author: Linh Vu Hong<lvho@dtu.dk> $
#-------------------------------------------------------------------------------
# Description: SublimeText plugin for RAISE Specification Language RSL
#     :copyright: Copyright 2013 by Linh Vu Hong
#     :license: BSD, see LICENSE for details.
#===============================================================================
import sublime, sublime_plugin, subprocess, re
from traceback import print_exc
from os.path import basename, splitext, dirname
from os import chdir, getcwd
from threading import Thread
import sys

ns = re.compile(r'[ \t\r\f\v]*--[ \t\r\f\v]*\n')

def rm(m):
	return ''

def dc(s):
	return s.decode('utf-8')

def rm_non_sense(s):
	sx = ns.sub(rm,s)
	return sx

def process_sml_output(s,fb):
	sml_open_re = re.compile(r'.*open %s\n' % (fb),re.DOTALL)
	s = sml_open_re.sub(rm,s)
	sml_val_re = re.compile(r'val it = \(\) : unit\n')
	s = sml_val_re.sub(rm,s)
	sml_warning = re.compile(r'X\.sml.*Warning: type vars.*',re.DOTALL)
	s = sml_warning.sub(rm,s)
	return s

def wrapped_exec(fn):
	""" Decorator for changing dir before and after execution
	"""
	def wrapper(self,edit):
		filename = self.view.file_name()
		if filename:
			fb =  basename(filename)
			d = dirname(filename)
			cdir = getcwd()
			# print("cd %s" % (d))
			chdir(d)
			fn(self,edit)
			# print("cd %s" % (cdir))
			chdir(cdir)
	return wrapper

def exec_cmd(cmd):
	rcode = None
	output = ""
	try:
		proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		output = proc.communicate()[0]
		rcode = proc.returncode
	except:
		print_exc(file=sys.stdout)
	return (rcode, dc(output))

class RslPrettyCommand(sublime_plugin.TextCommand):
	"""
	Pretty print
	"""
	@wrapped_exec
	def run(self, edit):
		r = sublime.Region(0, self.view.size())
		fn = basename(self.view.file_name())
		rulers = self.view.settings().get('rulers',[80])
		# print(rulers)
		ruler = rulers[0] - 2
		try:
			(rcode, output) = exec_cmd(["rsltc","-pl",str(ruler),fn])
			if rcode:
				print(output)
			else:
				cleaned = rm_non_sense(output)
				self.view.replace(edit, r, cleaned)
		except:
			print_exc(file=sys.stdout)

class RslTypeCheckCommand(sublime_plugin.TextCommand):
	"""
	Type check using rsltc
	"""
	@wrapped_exec
	def run(self, edit):
		fn = self.view.file_name()
		fb = basename(fn)
		(rcode, output) = exec_cmd(["rsltc",fb])
		print(output)

class RslToSmlCommand(sublime_plugin.TextCommand):
	"""
	Translate RSL to SML
	"""
	@wrapped_exec
	def run(self, edit):
		fn =  basename(self.view.file_name())
		(rcode, output) = exec_cmd(["rsltc","-m",fn])
		fx = splitext(fn)[0]+".sml"
		with open(fx,"a") as f:
			f.write("OS.Process.exit(OS.Process.success)")
		print(output)

class RslRunSmlCommand(sublime_plugin.TextCommand):
	"""
	Run SML and save results
	"""
	@wrapped_exec
	def run(self, edit):
		fn =  basename(self.view.file_name())
		b = splitext(fn)[0]
		fx = b+".sml"
		rf = b+".sml-results"
		(rcode, output) = exec_cmd(["sml",fx])
		if rcode == 0:
			output = process_sml_output(output,b)
			with open(rf,'w') as f:
				f.write(output)
		print(output)
		print("Run SML finished. Results are saved in %s" % (rf))

class RslToSalCommand(sublime_plugin.TextCommand):
	"""
	Translate RSL to SAL
	"""
	@wrapped_exec
	def run(self, edit):
		fn =  basename(self.view.file_name())
		(rcode, output) = exec_cmd(["rsltc","-sal",fn])
		print(output)

class RslRunSalWfcCommand(sublime_plugin.TextCommand):
	"""
	Run SAL wellform checker
	"""
	@wrapped_exec
	def run(self, edit):
		fn =  basename(self.view.file_name())
		b = splitext(fn)[0]
		(rcode, output) = exec_cmd(["sal-wfc",b])
		print(output)

class RslRunSalDeadlockCheckerCommand(sublime_plugin.TextCommand):
	"""
	Run SAL deadlock checker
	"""
	def make_cmd(self):
		cmd = []
		fn =  basename(self.view.file_name())
		d = dirname(self.view.file_name())
		b = splitext(fn)[0]
		r = sublime.Region(0, self.view.size())
		s = self.view.substr(r)
		m = re.search('transition_system\s*\[(.*)\]\s*local',s)
		if m:
			tname = m.group(1)
			cmd = ["sal-deadlock-checker",b,tname]
		else:
			self.view.set_status('RSL',"No transition system found in %s" %(fn))
		return (d,cmd)

	def process_output(self,output):
		print(output)

	def run(self, edit):
		(d,cmd) = self.make_cmd()
		if cmd: 
			threads = []
			thread = RslSalThreadCall(cmd,d)
			threads.append(thread)
			thread.start()
			self.handle_threads(threads)

	def handle_threads(self, threads):
		next_threads = []
		for thread in threads:
			if thread.is_alive():
				next_threads.append(thread)
				continue
			if thread.rcode == 0:
				self.process_output(thread.output)
		threads = next_threads
		if len(threads):
			self.view.set_status('RSL','SAL is running...')
			sublime.set_timeout(lambda: self.handle_threads(threads), 1000)
		else:
			self.view.set_status('RSL','SAL is done...')

class RslRunSalSmcCommand(RslRunSalDeadlockCheckerCommand):
	"""
	Run SAL symbolic model checker
	"""
	def make_cmd(self):
		fn =  basename(self.view.file_name())
		d = dirname(self.view.file_name())
		b = splitext(fn)[0]
		fx = b+".sal"
		rf = b+".sal-smc"
		cmd = ["sal-smc","-v1","--delta-path",fx]
		return (d,cmd)

	@wrapped_exec
	def process_output(self, output):
		fn =  basename(self.view.file_name())
		b = splitext(fn)[0]
		rf = b+".sal-smc"
		with open(rf,'w') as f:
			f.write(output)
		print(output)
		print("Run SAL-SMC finished. Results are saved in %s" % (rf))

class RslSalThreadCall(Thread):
	"""
	Run RSL SAL command in a thread so we dont block the UI
	"""
	def __init__(self,cmd,directory):
		self.cmd = cmd
		self.rcode = None
		self.output = None
		self.directory = directory
		Thread.__init__(self)

	def run(self):
		if self.directory:
			chdir(self.directory)
		(rcode, output) = exec_cmd(self.cmd)
		self.rcode = rcode
		self.output = output

class RslJoinCommentsCommand(sublime_plugin.TextCommand):
    """ Join two or more line comments into a block comment """
    def run(self,edit):
        regions = []
        for r in self.view.sel():
            regions.append(r)
        allbuffer = sublime.Region(0, self.view.size())
        old_viewport_position = self.view.viewport_position()
        buf = self.view.substr(allbuffer)
        newbuf = self._join_comments(buf)
        # print(newbuf)
        self.view.replace(
            edit, allbuffer,
            newbuf)
        self.view.sel().clear()
        for r in regions:
          self.view.sel().add(r)
        # FIXME: Without the 10ms delay, the viewport sometimes jumps.
        sublime.set_timeout(lambda: self.view.set_viewport_position(
            old_viewport_position, False), 10)
        
    def _join_comments(self,str):
        return re.sub(r"(^\s*\-\-.+\n)(^\s*\-\-.+\n|^\s*\n)*",self._join, str,flags=re.MULTILINE)

    def _join(self,m):
        s = m.group(0)
        ls = s.split("\n")
        ls = [ re.sub(r"^[\s-]+","",l[2:].rstrip()) for l in ls if len(l.strip()) > 0]
        return "/* %s */\n" % ('\n * '.join(ls))
        # return s
