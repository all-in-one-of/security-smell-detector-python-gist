#! /usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Generate an HTML Snippet for WordPress Blogs from reStructuredText.
#
# This is a modification of the standard HTML writer that leaves out
# the header, the body tag, and several CSS classes that have no use
# in wordpress. What is left is an incomplete HTML document suitable
# for pasting into the WordPress online editor.
#
# Note: This is a quick hack, so it probably won't work for the more
#       advanced features of rst.
#
# Copyright (c) 2008 Matthias Friedrich <matt AT mafr D:O:T de>
# Modified by Manuel Vázquez Acosta <mva.led A@T gmail DOT com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the Artistic License.
#
import sys
import docutils
import docutils.nodes
from docutils.writers import html4css1
from docutils import frontend, writers
from docutils.core import publish_cmdline, default_description
from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives

class sourcecode_node(nodes.comment): 
	def __init__(self, **opts):
		nodes.comment.__init__(self, **opts)
		self.language = opts.get("language", None)
		

class SourcecodeDirective(rst.Directive):
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}
    has_content = False
    node_class = sourcecode_node

    def run(self):
	    language = directives.uri(self.arguments[0])
	    self.options['language'] = language
	    node = sourcecode_node(rawsource=self.block_text,
				   **self.options)
	    return [node]



directives.register_directive("sourcecode", SourcecodeDirective)

class Writer(html4css1.Writer):
	supported = ('wphtml', )

	settings_spec = html4css1.Writer.settings_spec + ( )

	def __init__(self):
		html4css1.Writer.__init__(self)
		self.translator_class = WpHtmlTranslator


class WpHtmlTranslator(html4css1.HTMLTranslator):
	"""An HTML emitting visitor."""

	doctype = ('')

	def __init__(self, *args):
		html4css1.HTMLTranslator.__init__(self, *args)
		self.stylesheet = [ ]
		self.meta = [ ]
		self.head = [ ]
		self.head_prefix = [ ]
		self.body_prefix = [ ]
		self.body_suffix = [ ]
		self.section_level = 2
		self.compact_simple = True
		self.literal_block = False
		self.sourcecode = None


	def visit_document(self, node):
		pass

	def depart_document(self, node):
		pass

	def visit_section(self, node):
		self.section_level += 1

	def depart_section(self, node):
		self.section_level -= 1

	def visit_paragraph(self, node):
		if self.should_be_compact_paragraph(node):
			self.context.append('')
		else:
			self.body.append('')
			self.context.append('\n\n')

	def depart_paragraph(self, node):
		self.body.append(self.context.pop())

	def visit_reference(self, node):
		attrs = { }
		if node.has_key('refuri'):
			attrs['href'] = node['refuri']
		else:
			assert node.has_key('refid'), 'Invalid internal link'
			attrs['href'] = '#' + node['refid']
		self.body.append(self.starttag(node, 'a', '', **attrs))

	def visit_Text(self, node):
		if self.literal_block:
			text = node.astext()
		else:
			text = node.astext().replace('\n', ' ')
		# XXX: Should not emit &quot;
		encoded = text # self.encode(text)
		if self.in_mailto and self.settings.cloak_email_addresses:
			encoded = self.encode(text)
			encoded = self.cloak_email(encoded)
		self.body.append(encoded)

	def visit_block_quote(self, node):
		self.body.append('\n')

	def depart_block_quote(self, node):
		self.body.append('\n')

	def visit_list_item(self, node):
		self.body.append('  ' + self.starttag(node, 'li', ''))

	def visit_title(self, node):
		h_level = self.section_level + self.initial_header_level - 1
		self.body.append(
			self.starttag(node, 'h%s' % h_level, '', **{ }))
		self.context.append('</h%s>\n\n' % (h_level, ))

	def depart_title(self, node):
		self.body.append(self.context.pop())

	def visit_literal_block(self, node):
		self.literal_block = True
		if self.sourcecode:
			self.body.append('\n[sourcecode language="%s"]\n' % self.sourcecode)
		else:
			self.body.append(self.starttag(node, 'pre'))

	def depart_literal_block(self, node):
		if self.sourcecode:
			self.body.append('\n[/sourcecode]\n\n')
		else:
			self.body.append('\n</pre>\n\n')
		self.literal_block = False

	def visit_literal(self, node):
		self.body.append('<code>')

	def depart_literal(self, node):
		self.body.append('</code>')

	def visit_sourcecode_node(self, node):
		self.sourcecode = node.language

	def depart_sourcecode_node(self, node):
		pass


if __name__ == '__main__':
	# docutils tries to load the module 'wphtml' below, so we need an alias
	sys.modules['wphtml'] = sys.modules['__main__']

	try:
	    import locale
	    locale.setlocale(locale.LC_ALL, '')
	except:
	    pass

	description = ('Generates an HTML Snippet for Wordpress from'
			'standalone reStructuredText sources.  '
			+ default_description)

	publish_cmdline(writer_name='wphtml', description=description)

# EOF
