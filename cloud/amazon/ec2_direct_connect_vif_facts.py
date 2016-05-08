#!/usr/bin/python
#
# This is a free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This Ansible library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: ec2_direct_connect_vif_facts
short_description: Gather facts about virtual interfaces for direct connect connections
description:
    - Gather facts about virtual interfaces for direct connect connections
version_added: "2.2"
requirements: [ boto3 ]
author: "Nick Aslanidis (@naslanidis)"
options:
  connectionId:
    description:
      - Get virtual interfaces for a specific direct connect connection id
      - Provide this value as a string
    required: false
    default: None
  virtualInterfaceId:
    description:
      - Get virtual interface facts for a specific virtual interface id
      - Provide this value as a string
    required: false
    default: None
extends_documentation_fragment:
    - aws
    - ec2
'''

EXAMPLES = '''
# # Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Gather facts about all direct connect virtual interfaces for an account or profile
  ec2_direct_connect_vif_facts:
    region: ap-southeast-2
    profile: production
  register: dc_vif_facts

- name: Gather facts about virtual interfaces for a specific direct connect connection id
  ec2_direct_connect_vif_facts:
    region: ap-southeast-2
    profile: production
    connectionId: dxcon-fgwr13cd
  register: dc_vif_facts

- name: Gather virtual interface facts for a specific virtual interface id
  ec2_direct_connect_vif_facts:
    region: ap-southeast-2
    profile: production
    virtualInterfaceId: dxvif-ffh2k3n3
  register: dc_vif_facts

'''

RETURN = '''
direct_connect_vifs:
    description: The list of direct connect vif facts
    returned: always
    type: list

changed:
    description: True if listing the direct connect vifs succeeds
    type: bool
    returned: always
'''

import json

try:
    import botocore
    import boto3  
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


def get_dc_vifs_info(dc_vif):
    dc_vif_info = {'ownerAccount': dc_vif['ownerAccount'],
                   'virtualInterfaceId': dc_vif['virtualInterfaceId'],
                   'location': dc_vif['location'],
                   'connectionId': dc_vif['connectionId'],
                   'virtualInterfaceType': dc_vif['virtualInterfaceType'],
                   'virtualInterfaceName': dc_vif['virtualInterfaceName'],
                   'vlan': dc_vif['vlan'],
                   'asn': dc_vif['asn'],
                   'authKey': None,
                   'amazonAddress': dc_vif['amazonAddress'],
                   'customerAddress': dc_vif['customerAddress'],
                   'virtualInterfaceState': dc_vif['virtualInterfaceState'],
                   'customerRouterConfig': None,
                   'virtualGatewayId': None,
                   'routeFilterPrefixes': dc_vif['routeFilterPrefixes']
                  }
    
    if 'authKey' in dc_vif.keys():
        dc_vif_info['authKey'] = dc_vif['authKey']

    if 'customerRouterConfig' in dc_vif.keys():
        dc_vif_info['customerRouterConfig'] = dc_vif['customerRouterConfig']

    if 'virtualGatewayId' in dc_vif.keys():
        dc_vif_info['virtualGatewayId'] = dc_vif['virtualGatewayId']

    return dc_vif_info


def list_dc_vifs(client, module):
    all_dc_vifs_array = []
    params = dict()

    if module.params.get("connectionId"):
        params['connectionId'] = module.params.get("connectionId")

    if module.params.get("virtualInterfaceId"):
        params['virtualInterfaceId'] = module.params.get("virtualInterfaceId")

    try:
        all_dc_vifs = client.describe_virtual_interfaces(**params)
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg=str(e))

    for dc_vif in all_dc_vifs['virtualInterfaces']:
        all_dc_vifs_array.append(get_dc_vifs_info(dc_vif))

    snaked_dc_vifs_array = []
    for vif in all_dc_vifs_array:
        snaked_dc_vifs_array.append(camel_dict_to_snake_dict(vif))
    
    module.exit_json(direct_connect_vifs=snaked_dc_vifs_array)


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            connectionId = dict(),
            virtualInterfaceId = dict()
        )
    )

    module = AnsibleModule(argument_spec=argument_spec)

     # Validate Requirements
    if not HAS_BOTO3:
        module.fail_json(msg='json and botocore/boto3 is required.')

    try:
        region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        connection = boto3_conn(module, conn_type='client', resource='directconnect', region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except botocore.exceptions.NoCredentialsError, e:
        module.fail_json(msg="Can't authorize connection - "+str(e))

    # call your function here
    results = list_dc_vifs(connection, module)

    module.exit_json(result=results)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()
