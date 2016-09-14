#coding:utf-8
from txweb import btforms
from txweb.btforms import rules
from txweb.btforms.rules import button_style,input_style

boolean = {0:u"否", 1:u"是"}
booleans = {'0': u"否", '1': u"是"}

sys_form = btforms.Form(
    btforms.Textbox("system_name", description=u"系统名称",help=u"管理系统名称,可以根据你的实际情况进行定制", **input_style),
    btforms.Button("submit", type="submit", html=u"<b>更新</b>", **button_style),
    title=u"参数配置管理",
    action="/admin/param/update?active=syscfg"
)










