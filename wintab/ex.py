import os, math, sys, re, json, shutil
from functools import partial
from typing import Sequence, TypeVar, Callable, Union, List, Mapping, Dict, Any, TypeAlias

T = TypeVar("T")
Record = Dict[str, Any]
RoRecord = Mapping[str, Any]
KeyListLike = Union[str, Sequence[str]]
N: TypeAlias = Union[None, T]


def _parse_keys_like_str(s: KeyListLike):
    if isinstance(s, str):
        return s.split(" ")
    return s


class exlist:

    @staticmethod
    def get(arr: Sequence[T], match: Callable[[T], bool]):
        for item in arr:
            if match(item):
                return item
        return None

    @staticmethod
    def index(arr: Sequence[T], match: Callable[[T], bool]):
        for index, item in enumerate(arr):
            if match(item):
                return index
        return -1

    @staticmethod
    def pick(arr: Sequence[T], match: Callable[[T], bool]) -> List[T]:
        new_arr = []
        for item in arr:
            if match(item):
                new_arr.append(item)
        return new_arr

    @staticmethod
    def omit(arr: Sequence[T], match: Callable[[T], bool]) -> List[T]:
        new_arr = []
        for item in arr:
            if not match(item):
                new_arr.append(item)
        return new_arr

    @staticmethod
    def unique(arr: Sequence[T]) -> List[T]:
        s = set()
        a = []
        for i in arr:
            if i not in s:
                a.append(i)
                s.add(i)
        return a

    @staticmethod
    def diff(target, ref, key):
        """比较两个数组。Returns `(created, removed, other_target, other_ref)`"""
        created, removed, other_t, other_r = [], [], [], []
        tks = [key(d) for d in target]
        rks = [key(d) for d in ref]
        tqd = {k: d for k, d in zip(tks, target)}
        rqd = {k: d for k, d in zip(rks, ref)}
        for k in tks:
            if k not in rqd:
                created.append(tqd[k])
            else:
                other_t.append(tqd[k])
        for k in rks:
            if k not in tqd:
                removed.append(rqd[k])
            else:
                other_r.append(rqd[k])
        return created, removed, other_t, other_r

    @staticmethod
    def expand_id_list(arr: Sequence[Union[int, str]]):
        rd = []
        for i in arr:
            if isinstance(i, int):
                rd.append(i)
            elif isinstance(i, str):
                x = i.replace(" ", "")
                if "-" in x:
                    start, end = x.split("-")
                    for j in range(int(start), int(end) + 1):
                        rd.append(j)
                else:
                    rd.append(int(x))
        return rd


class exdict:

    @staticmethod
    def pick_by(data, func):
        return {k: v for k, v in data.items() if func(k, v)}

    @staticmethod
    def pick_keys(dct: RoRecord, keys: KeyListLike, allow_none=False):
        new_dct: Record = {}
        for k in _parse_keys_like_str(keys):
            if k in dct:
                new_dct[k] = dct[k]
            elif allow_none:
                new_dct[k] = None
        return new_dct

    @staticmethod
    def pick_keys_with_defaults(dct, keys, defaults):
        data = exdict.pick_keys(dct, keys)
        for k in defaults:
            if k not in data:
                data[k] = defaults[k]
        return data

    @staticmethod
    def pick_attrs(obj, keys: KeyListLike, allow_none=False):
        new_dct: Record = {}
        for k in _parse_keys_like_str(keys):
            if hasattr(obj, k):
                new_dct[k] = getattr(obj, k)
            elif allow_none:
                new_dct[k] = None
        return new_dct

    @staticmethod
    def omit_keys(dct: RoRecord, keys: KeyListLike):
        new_dct: Record = {}
        kset = _parse_keys_like_str(keys)
        for k in dct.keys():
            if k not in kset:
                new_dct[k] = dct[k]
        return new_dct

    @staticmethod
    def pop_keys(dct: Record, keys: KeyListLike):
        return {k: dct.pop(k) for k in _parse_keys_like_str(keys) if k in dct}

    @staticmethod
    def assign(target: Record, source: RoRecord, overwrite=True):
        for k in source.keys():
            if k in target:
                if overwrite:
                    target[k] = source[k]
            else:
                target[k] = source[k]
        return target

    @staticmethod
    def update_recursively(target: Record, source: RoRecord):
        """递归更新（仅字典执行递归，数组直接覆盖）"""
        for k in source.keys():
            if k in target and isinstance(target[k], dict):
                target[k] = exdict.update_recursively(target[k], source[k])
            else:
                target[k] = source[k]
        return target

    @staticmethod
    def diff(target, ref):
        nd = {}
        od = {}
        for k in target:
            if k in ref:
                if isinstance(target[k], dict):
                    nd[k], od[k] = exdict.diff(target[k], ref[k])
                elif target[k] != ref[k]:
                    nd[k] = target[k]
                    od[k] = ref[k]
            else:
                od[k] = target[k]
        for k in ref:
            if k not in target:
                nd[k] = ref[k]
        return nd, od


class expath:
    join = os.path.join
    exists = os.path.exists
    basename = os.path.basename
    dirname = os.path.dirname
    splitext = os.path.splitext
    abspath = os.path.abspath

    @staticmethod
    def getFileSize(filepath: str):
        return os.path.getsize(filepath)

    @staticmethod
    def formatFileSize(nbytes: int, sep=" "):
        v = lambda n, u: f"{n}{sep}{u}"
        if nbytes == 0:
            return v(0, "B")
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(nbytes, 1024)))
        p = math.pow(1024, i)
        s = round(nbytes / p, 2)
        return v(s, size_name[i])

    @staticmethod
    def getFormattedFileSize(filepath: str, sep=" "):
        nbytes = expath.getFileSize(filepath)
        sbytes = expath.formatFileSize(nbytes, sep=sep)
        return nbytes, sbytes

    @staticmethod
    def mkdir(*paths, recurse=True) -> str:
        path = os.path.join(*paths)
        if not os.path.exists(path):
            if recurse:
                os.makedirs(path)
            else:
                os.mkdir(path)
        return path


class exfs:
    remove_file = os.remove
    remove_dir = shutil.rmtree
    make_dir = expath.mkdir
    make_soft_link = os.symlink
    make_hard_link = os.link


class exsys:

    @staticmethod
    def exit(msg: str, exitcode=1):
        """打印错误消息并退出"""
        print(f"[EXIT] {exitcode} {msg}")
        sys.exit(exitcode)


class exos:

    @staticmethod
    def list_files(target_dir: str, pattern: str, exclude_dirs: N[Sequence[str]] = None):
        items = []
        index = 0
        exclude_dir_set = set(exclude_dirs or [])
        for dp, _, fns in os.walk(target_dir):
            dp_n = os.path.basename(dp)
            if dp_n in exclude_dir_set:
                continue
            for fn in fns:
                if mt := re.match(pattern, fn):
                    item = {"id": index, "fn": fn, "dp": dp, "mt": mt.groups()}
                    items.append(item)
                    index += 1
        return items


class exio:

    json_load = json.load
    json_loads = json.loads
    json_dump = json.dumps
    json_dumps = json.dumps

    @staticmethod
    def read(filepath: str):
        with open(filepath) as fr:
            return fr.read()

    @staticmethod
    def write(content: str, filepath: str):
        with open(filepath, "w") as fw:
            fw.write(content)

    @staticmethod
    def read_json(filepath: str, default=None):
        if not os.path.exists(filepath):
            return default
        with open(filepath) as fr:
            return json.load(fr)

    @staticmethod
    def write_json(data: T, filepath: str, **options):
        with open(filepath, "w") as fw:
            json.dump(data, fw, **options)


class exstd:

    @staticmethod
    def write_datline(key: str, data: T, **options):
        jstr = json.dumps(data, **options)
        ostr = f"::{key}::{jstr}"
        print(ostr, flush=True)

    @staticmethod
    def read_datline(text: str):
        if mt := re.match(r"::(\w+?)::(.*)", text):
            key = mt.group(1)
            jstr = mt.group(2)
            data = json.loads(jstr)
            return key, data
        else:
            return None, text


class exstr:

    @staticmethod
    def as_variable_name(s: str):
        """将字符串转换为Python的合法变量名称"""
        import keyword

        # 移除非法字符并替换为下划线
        valid_string = re.sub(r"\W+", "_", s)

        # 如果字符串以数字开头，则在开头添加下划线
        if valid_string[0].isdigit():
            valid_string = "_" + valid_string

        # 如果字符串是Python的关键字，则在末尾添加下划线
        if keyword.iskeyword(valid_string):
            valid_string += "_"

        return valid_string

    @staticmethod
    def hash16(text: str):
        import hashlib

        # 使用SHA256哈希算法
        hash_object = hashlib.sha256(text.encode("utf-8"))
        # 获取哈希值的十六进制表示
        hash_hex = hash_object.hexdigest()
        # 截取前16个字符，并转换为大写
        result = hash_hex[:16].upper()
        return result

    @staticmethod
    def rstr(size: int):
        import random, string

        letters = string.ascii_letters
        return "".join(random.sample(letters, size))

    @staticmethod
    def is_valid_variable_name(variable_name: str):
        import keyword

        if keyword.iskeyword(variable_name):
            return False
        if variable_name.isidentifier():
            return True
        return False


class Singleton:
    __singleton_instance__ = None

    def __new__(cls, *args, **kwargs):
        if cls.__singleton_instance__ is None:
            cls.__singleton_instance__ = super().__new__(cls, *args, **kwargs)
        return cls.__singleton_instance__
