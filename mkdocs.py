from docstr_md.python import PySoup, compile_md
from docstr_md.src_href import Github

src_href = Github('https://github.com/dsbowen/flask-worker/blob/master')

path = 'flask_worker/__init__.py'
soup = PySoup(path=path, parser='sklearn', src_href=src_href)
soup.rm_properties()
compile_md(soup, compiler='sklearn', outfile='docs_md/manager.md')

path = 'flask_worker/worker_mixin.py'
soup = PySoup(path=path, parser='sklearn', src_href=src_href)
soup.rm_properties()
soup.import_path = 'flask_worker'
compile_md(soup, compiler='sklearn', outfile='docs_md/worker_mixin.md')

path = 'flask_worker/router_mixin.py'
soup = PySoup(path=path, parser='sklearn', src_href=src_href)
soup.rm_properties()
soup.import_path = 'flask_worker'
compile_md(soup, compiler='sklearn', outfile='docs_md/router_mixin.md')