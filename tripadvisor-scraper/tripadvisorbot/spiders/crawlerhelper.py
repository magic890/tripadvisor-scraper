import HTMLParser
import unicodedata

htmlparser = HTMLParser.HTMLParser()

def is_ascii(s):
	return all(ord(c) < 128 for c in s)

def clean_parsed_string(string):
	if len(string) > 0:
		ascii_string = string
		if is_ascii(ascii_string) == False:
			ascii_string = unicodedata.normalize('NFKD', ascii_string).encode('ascii', 'ignore')
		return str(ascii_string)
	else:
		return None

def get_parsed_string(selector, xpath):
	return_string = ''
	extracted_list = selector.xpath(xpath).extract()
	if len(extracted_list) > 0:
		raw_string = extracted_list[0].strip()
		if raw_string is not None:
			return_string = htmlparser.unescape(raw_string)
	return return_string

def get_parsed_string_multiple(selector, xpath):
	return_string = ''
	return selector.xpath(xpath).extract()