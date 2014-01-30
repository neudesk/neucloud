from keystoneclient.v2_0 import Client
from django.conf import settings

class KeystoneCli(object):

    def __init__(self):
        self.auth_url = getattr(settings, 'OPENSTACK_KEYSTONE_URL', None)
        self.adm_tenant = getattr(settings, 'OPENSTACK_ADMIN_DEF_PROJ', None)
        self.adm_user = getattr(settings, 'OPENSTACK_ADMIN', None)
        self.adm_pw = getattr(settings, 'OPENSTACK_ADMIN_PASS', None)
        self.client = Client(username=self.adm_user,
                             password=self.adm_pw,
                             tenant_name=self.adm_tenant,
                             auth_url=self.auth_url)

    def make_tenant(self, tenant_name=None, description=None, enabled=False):
        tenant = self.client.tenants.create(tenant_name,
                                            description=description,
                                            enabled=enabled)
        return tenant

    def make_user(self, name=None, password=None, email=None, tenant_id=None, enabled=False):
        user = self.client.users.create(name,
                                        password,
                                        email=email,
                                        tenant_id=tenant_id,
                                        enabled=enabled)
        return user