#Zscaler Tools
Python Library used for interacting with Zscaler's public API

How to install:
```
pip install -- index-url https://test.pypi.org/simple/ zscalertools
```

How to use:
```
import zscalertools
ztoolsinstance = zscalertools.api.zia('admin.zscalerbeta.net', 'test_api@user.com', 'password', 'Apikey')

ztoolsinstance.get_users()
```