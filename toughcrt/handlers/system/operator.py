#!/usr/bin/env python
# coding:utf-8

from txweb.permit import permit
from toughcrt.common import tools
from toughcrt import models
from toughcrt.handlers.base import BaseHandler,MenuSys
from toughcrt.handlers.base import authenticated
from toughcrt.handlers.system import operator_form
from txweb import dispatch,redis_cache,logger,utils


@permit.route(r"/admin/operator", u"操作员管理", MenuSys, order=3.0000, is_menu=True)
class OperatorHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render("operator_list.html",
                      operator_list=self.db.query(models.SysOperator),opr_status=operator_form.opr_status_dict)


@permit.route(r"/admin/operator/add", u"操作员新增", MenuSys, order=3.0001)
class AddHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render("opr_form.html", form=operator_form.operator_add_form(),rules=[])

    @authenticated
    def post(self):
        form = operator_form.operator_add_form()
        if not form.validates(source=self.get_params()):
            return self.render("base_form.html", form=form)
        if self.db.query(models.SysOperator.id).filter_by(operator_name=form.d.operator_name).count() > 0:
            return self.render("base_form.html", form=form, msg=u"操作员已经存在")
        operator = models.SysOperator()
        operator.operator_name = form.d.operator_name
        operator.operator_pass = tools.saltmd5(form.d.operator_pass.encode())
        operator.operator_type = 1
        operator.operator_desc = form.d.operator_desc
        operator.operator_status = form.d.operator_status
        self.db.add(operator)

        self.add_oplog(u'新增操作员信息:%s' % utils.safeunicode(operator.operator_name))

        for path in self.get_arguments("rule_item"):
            item = permit.get_route(path)
            if not item: continue
            rule = models.SysOperatorRule()
            rule.operator_name = operator.operator_name
            rule.rule_name = item['name']
            rule.rule_path = item['path']
            rule.rule_category = item['category']
            self.db.add(rule)

        self.db.commit()

        for rule in self.db.query(models.SysOperatorRule).filter_by(operator_name=operator.operator_name):
            permit.bind_opr(rule.operator_name, rule.rule_path)

        self.redirect("/admin/operator",permanent=False)

@permit.route(r"/admin/operator/update", u"操作员修改", MenuSys, order=3.0002)
class UpdateHandler(BaseHandler):
    @authenticated
    def get(self):
        operator_id = self.get_argument("operator_id")
        opr = self.db.query(models.SysOperator).get(operator_id)
        form = operator_form.operator_update_form()
        form.fill(self.db.query(models.SysOperator).get(operator_id))
        form.operator_pass.set_value('')

        rules = self.db.query(models.SysOperatorRule.rule_path).filter_by(operator_name=opr.operator_name)
        rules = [r[0] for r in rules]
        return self.render("opr_form.html", form=form, rules=rules)

    @authenticated
    def post(self):
        form = operator_form.operator_update_form()
        if not form.validates(source=self.get_params()):
            rules = self.db.query(models.SysOperatorRule.rule_path).filter_by(operator_name=form.d.operator_name)
            rules = [r[0] for r in rules]
            return self.render("base_form.html", form=form,rules=rules)
        operator = self.db.query(models.SysOperator).get(form.d.id)
        if form.d.operator_pass:
            operator.operator_pass = tools.saltmd5(form.d.operator_pass.encode())
        operator.operator_desc = form.d.operator_desc
        operator.operator_status = form.d.operator_status

        self.add_oplog(u'修改操作员%s信息' % utils.safeunicode(operator.operator_name))

        # update rules
        self.db.query(models.SysOperatorRule).filter_by(operator_name=operator.operator_name).delete()

        for path in self.get_arguments("rule_item"):
            item = permit.get_route(path)
            if not item: continue
            rule = models.SysOperatorRule()
            rule.operator_name = operator.operator_name
            rule.rule_name = item['name']
            rule.rule_path = item['path']
            rule.rule_category = item['category']
            self.db.add(rule)

        permit.unbind_opr(operator.operator_name)

        self.db.commit()

        for rule in self.db.query(models.SysOperatorRule).filter_by(operator_name=operator.operator_name):
            permit.bind_opr(rule.operator_name, rule.rule_path)

        self.redirect("/admin/operator",permanent=False)

@permit.route(r"/admin/operator/delete", u"操作员删除", MenuSys, order=3.0003)
class DeleteHandler(BaseHandler):

    @authenticated
    def get(self):
        operator_id = self.get_argument("operator_id")
        opr = self.db.query(models.SysOperator).get(operator_id)
        self.db.query(models.SysOperatorRule).filter_by(operator_name=opr.operator_name).delete()
        self.db.query(models.SysOperator).filter_by(id=operator_id).delete()

        self.add_oplog(u'删除操作员%s信息' % utils.safeunicode(opr.operator_name))
        self.db.commit()
        self.redirect("/admin/operator",permanent=False)




