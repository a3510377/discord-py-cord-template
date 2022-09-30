import gettext

# cat = gettext.translation("test", "./data", ["zh_TW", "en_US"])
_ = gettext.gettext
print(_("hello world"))
