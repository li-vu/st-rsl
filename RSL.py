# -*- coding: utf-8 -*-
""" 
    SublimeText plugin for RAISE Specification Language RSL
    ~~~~~~~~~~~~~~~~~~~
    Author: Linh Vu Hong <lvho@dtu.dk>

    :copyright: Copyright 2013 by Linh Vu Hong
    :license: BSD, see LICENSE for details.
"""
import sublime, sublime_plugin, subprocess, re
from traceback import print_exc
from os.path import basename, splitext, dirname
from os import chdir, getcwd
import sys

ns = re.compile(r'[ \t\r\f\v]*--[ \t\r\f\v]*\n')

def rm(m):
	return ''

def rm_non_sense(str):
	str = ns.sub(rm,str)
	return str

def process_sml_output(s,fb):
	sml_open_re = re.compile(r'.*open %s\n' % (fb),re.DOTALL)
	s = sml_open_re.sub(rm,s)
	sml_val_re = re.compile(r'val it = \(\) : unit\n')
	s = sml_val_re.sub(rm,s)
	sml_warning = re.compile(r'X\.sml.*Warning: type vars.*',re.DOTALL)
	s = sml_warning.sub(rm,s)
	return s
	
def prettyprint(view,edit):
	r = sublime.Region(0, view.size())
	fn = basename(view.file_name())
	try:
		(rcode, output) = exec_cmd(["rsltc","-p",fn])
		if rcode:
			print output
		else:
			cleaned = rm_non_sense(output)
			view.replace(edit, r, cleaned)
	except:
		pass

def wrapped_exec(fn):
	""" Decorator for changing dir before and after execution
	"""
	def wrapper(self,edit):
		filename = self.view.file_name()
		fb =  basename(filename)
		d = dirname(filename)
		cdir = getcwd()
		print "Change to %s" % (d)
		chdir(d)
		fn(self,edit)
		print "Change back to %s" % (cdir)
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
	return (rcode, output)

class RslPrettyCommand(sublime_plugin.TextCommand):
	@wrapped_exec
	def run(self, edit):
		e = self.view.begin_edit()
		prettyprint(self.view,e)
		self.view.end_edit(e)

class RslTypeCheckCommand(sublime_plugin.TextCommand):
	@wrapped_exec
	def run(self, edit):
		fn = self.view.file_name()
		fb = basename(fn)
		(rcode, output) = exec_cmd(["rsltc",fb])
		print output

class RslToSmlCommand(sublime_plugin.TextCommand):
	@wrapped_exec
	def run(self, edit):
		fn =  basename(self.view.file_name())
		(rcode, output) = exec_cmd(["rsltc","-m",fn])
		fx = splitext(fn)[0]+".sml"
		with open(fx,"a") as f:
			f.write("OS.Process.exit(OS.Process.success)")
		print output

class RslToSalCommand(sublime_plugin.TextCommand):
	@wrapped_exec
	def run(self, edit):
		fn =  basename(self.view.file_name())
		(rcode, output) = exec_cmd(["rsltc","-sal",fn])
		print output

class RslRunSmlCommand(sublime_plugin.TextCommand):
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
		print output
		print "Run SML finished. Results are saved in %s" % (rf)





