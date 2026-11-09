import urllib.request
import re

url = "https://www.classicartarchive.com"
html = urllib.request.urlopen(url).read().decode("utf-8")

matches = [m for m in re.findall(r'http://[^\s"\'<>]+', html) if not m.startswith('http://www.w3.org')]
print("Non-w3c http URLs found:", matches)

forms = re.findall(r'<form[^>]*>', html, re.I)
print("Forms found:", forms)

scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html, re.I)
print("External scripts:", scripts)

links = re.findall(r'<link[^>]*href=["\']([^"\']+)["\']', html, re.I)
print("External links:", links)
