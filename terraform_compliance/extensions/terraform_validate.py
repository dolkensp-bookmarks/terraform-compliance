import re
import sys


if sys.version_info[0] > 2:
    unicode = str


def enable_resource_mounting(tf_conf, processing_resource=None, resource=None):
    if not resource:
        resource = 'resource'
    else:
        resource = resource.strip()

    if not processing_resource:
        processing_resource = tf_conf[resource]

    source = resource.strip()
    source = (source[:-3] if source.endswith('.id') else source)

    for sub_resource, sub_value in processing_resource.items():

        if type(sub_value) is dict:
            enable_resource_mounting(tf_conf, sub_value, sub_resource)
        else:
            regex = r'\${(.*)\}'
            if type(sub_value) is str or type(sub_value) is unicode:
                matches = re.match(regex, sub_value)

                if matches is not None:
                    if not matches.group(1).startswith(('var', 'data', 'module')) and '(' not in matches.group(1):
                        target = matches.group(1).strip()
                        target = 'resource.{}'.format(target).split('.')
                        if target[-1] in ['id', 'name']:
                            target.pop(-1)

                        _change_value_in_dict(tf_conf, target, {source: processing_resource})

            elif type(sub_value) is list:
                for value in sub_value:
                    if type(value) is str or type(value) is unicode:
                        matches = re.match(regex, value)
                        if matches is not None:
                            if not matches.group(1).startswith(('var', 'data', 'module')) and '(' not in matches.group(1):
                                target = matches.group(1).strip()
                                target = 'resource.{}'.format(target).split('.')
                                if target[-1] in ['id', 'name']:
                                    target.pop(-1)

                                _change_value_in_dict(tf_conf, target, {source: processing_resource})


def _change_value_in_dict(target_dictionary, path_to_change, value_to_change):
    if type(path_to_change) is str:
        path_to_change = path_to_change.split('.')

    if type(path_to_change) is not list:
        return False

    path_to_adjust = '["{}"]'.format('"]["'.join(path_to_change))
    path_to_check  = '["{}"]["type"]'.format('"]["'.join(path_to_change))
    path_to_add    = '["{}"]'.format('"]["'.join(path_to_change[:-1]))


    try:
        target = eval('target_dictionary{}'.format(path_to_adjust))

        for key, value in value_to_change.items():
            if 'type' in value:
                type_key = value['type']
                source = value
                source['referenced_name'] = key

                if type_key not in target:
                    target[type_key] = list()
                elif type_key in target:
                    if type(target[type_key]) is not list:
                        target[type_key] = [target[type_key]]

                target[type_key].append(source)


        try:
            exec('target_dictionary{}.update({})'.format(path_to_adjust, target))
        except:
            # Yes I know, this is against PEP8.
            pass

    except KeyError:
        pass

