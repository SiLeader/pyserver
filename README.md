Web Server
==================

&copy; 2018 SiLeader.

## Overview


## Features
+ WSGI support
+ Static files support

## Settings
setting format is supporting JSON or TOML.

setting file specified by `-s` or `--setting` option.

```sh
PROGRAM --setting path/to/setting.toml path/to/setting.json
```

### Server types

| name | description |
|:----:|:------------|
| static | static file server (return file like html or css) |
| wsgi | WSGI server |

### Options
#### Common options

| option | required | type | description |
|:------:|:--------:|:----:|:------------|
| host | yes | str | host name (e.g. "localhost", "127.0.0.1") |
| port | yes | int | port number |
| headers | no | [str] or {str:str} | HTTP response header |
| options.version | no | bool | show server version in header (default=True) |

#### WSGI options

| option | required | type | description |
|:------:|:--------:|:----:|:------------|
| script | yes | str | script file name |
| object/app | yes | str | WSGI object name |
| package | yes | str | package directory path |

#### Static options

| option | required | type | description |
|:------:|:--------:|:----:|:------------|
| root | yes | str | document root |
| index | no | str | file name to be used when requested to the directory (default="index.html") |
| completion | no | str | automatically complement file extension (default=disabled) |

##### completion
ex1. completion = ".html"

`/index` =&gt; `index.html`  
`/index.html` =&gt; `index.html`

ex2. completion = "html"

`/index` =&gt; `index.html`  
`/index.html` =&gt; `index.html`

ex3. completion = ".css"

`/index` =&gt; `index.css`  
`/index.html` =&gt; `index.html`


## License
Apache License 2.0
