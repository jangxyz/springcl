__all__ = [
	'string_matching'
]
import re
from base import Matcher

class StringRegexMatcher(Matcher):
	def __init__(self, regex):
		self.desc_str = regex
		if isinstance(regex, str):
			regex = re.compile(regex)
		self.regex = regex
	
	def matches(self, other):
		return bool(self.regex.match(other))
	
	def desc(self):
		return "A string matching: %s" % (self.desc_str,)


string_matching = StringRegexMatcher

