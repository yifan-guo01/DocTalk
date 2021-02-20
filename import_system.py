import sys
import locale
print('local.getpreferredencoding:', locale.getpreferredencoding)
print('locale.getdefaultlocale:', locale.getdefaultlocale())
print('sys.stdout.encoding:', sys.stdout.encoding)
print('sys.getdefaultencoding:', sys.getdefaultencoding())
print('sys.getfilesystemencoding:', sys.getfilesystemencoding())