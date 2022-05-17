import datetime
import time
from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule  # type: ignore


def retry(exceptions, retries=20, delay=1):
    def decorator(f):
        def _retry(*args, **kwargs):
            _tries = retries
            while _tries > 1:
                try:
                    print("{}".format(_tries))
                    return f(*args, **kwargs)
                except exceptions:
                    time.sleep(delay)
                    _tries -= 1
            print("{} has failed after {} tries".format(f, retries))
            return f(*args, **kwargs)
        return _retry
    return decorator


def build_cmd(cli_binary: bool,
              cmd: str) -> List[str]:

    _cmd = []

    if not cli_binary:
        _cmd.extend(['cephadm', 'shell', 'ceph'])

    _cmd.extend(cmd.split(' '))

    return _cmd


def build_base_cmd(module: "AnsibleModule"):
    cmd = ['cephadm']
    if module.params.get('docker'):
        cmd.append('--docker')
    cmd.extend(['shell', 'ceph', 'orch'])
    return cmd


def exit_module(module: "AnsibleModule",
                rc: int, cmd: List[str],
                startd: datetime.datetime,
                out: str = '',
                err: str = '',
                changed: bool = False,
                diff: Dict[str, str] = dict(before="", after="")) -> None:
    endd = datetime.datetime.now()
    delta = endd - startd

    result = dict(
        cmd=cmd,
        start=str(startd),
        end=str(endd),
        delta=str(delta),
        rc=rc,
        stdout=out.rstrip("\r\n"),
        stderr=err.rstrip("\r\n"),
        changed=changed,
        diff=diff
    )
    module.exit_json(**result)


def fatal(message: str, module: "AnsibleModule") -> None:
    '''
    Report a fatal error and exit
    '''

    if module:
        module.fail_json(msg=message, rc=1)
    else:
        raise(Exception(message))
