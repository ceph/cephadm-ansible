import datetime
import time
from typing import TYPE_CHECKING, Any, List, Dict, Callable, Type, TypeVar

if TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule  # type: ignore

ExceptionType = TypeVar('ExceptionType', bound=BaseException)


def retry(exceptions: Type[ExceptionType], retries: int = 20, delay: int = 1) -> Callable:
    def decorator(f: Callable) -> Callable:
        def _retry(*args: Any, **kwargs: Any) -> Callable:
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


def build_base_cmd(module: "AnsibleModule") -> List[str]:
    cmd = ['cephadm']
    docker = module.params.get('docker')
    image = module.params.get('image')

    if docker:
        cmd.append('--docker')
    if image:
        cmd.extend(['--image', image])

    return cmd


def build_base_cmd_shell(module: "AnsibleModule") -> List[str]:
    cmd = build_base_cmd(module)
    fsid = module.params.get('fsid')

    cmd.append('shell')

    if fsid:
        cmd.extend(['--fsid', fsid])

    return cmd


def build_base_cmd_orch(module: "AnsibleModule") -> List[str]:
    cmd = build_base_cmd_shell(module)
    cmd.extend(['ceph', 'orch'])

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
        raise Exception(message)
