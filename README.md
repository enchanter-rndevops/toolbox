# TOOLBOX

開発に使用すると便利だと思われるPythonスクリプトをまとめているプロジェクト。

スクリプトのリスト

* **[sgzu](./sgzu/README.md)**
  セキュリティグループの図(mermaidダイアグラム)を自動生成する。
* **[storeparam](./storeparam/README.md)**
  ローカルにあるプロパティファイルをAWSパラメータストアに投入するスクリプト。

## ツールを使う

pyenvとpipxを使用し、コマンドのように使えるようにします。

### Pythonのインストール

Pythonの管理には pyenv を推奨しています。 
システムの Python を利用する場合は、この手順を行う必要はありません。

```bash
# Pythonのビルドに必要なパッケージのインストール
$sudo apt update && sudo apt install -y \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    curl \
    git \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev
# pyenvのインストール
$ curl https://pyenv.run | bash    
# pyenvの設定を .bashrc に追加し、適用する。
$ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
$ echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
$ echo 'eval "$(pyenv init -)"' >> ~/.bashrc
$ source ~/.bashrc
# インストール可能なバージョンを確認
$ pyenv install --list | grep " 3.1."
# 特定のバージョンをインストール。ソースからビルドするので、少々時間がかかる。
$ pyenv install 3.15.2
# 全体で使うPythonのバージョンを設定
$ pyenv global 3.15.2
# 特定のプロジェクトディレクトリ内でのみ使う場合
# cd /path/to/your/project
# pyenv local 3.15.2
```

## pipxを使う

pipx を利用すると、各ツールを独立した仮想環境にインストールし、コマンドとして実行できます。
ここでは行いませんが、使用するpythonのバージョンを変更することもできます。

### pipxのインストール

```bash
$ sudo apt update && sudo apt install pipx -y
```

### toolboxのインストール

pyproject.tomlにあるパッケージをコマンドのように使用することができます。

```
$ git clone https://github.com/enchanter-rndevops/toolbox.git
$ cd toolbox
$ pipx install --editable .
```

新しいコマンドが追加されたら、最新のソースを取得し、パッケージをインストールしてください。

```bash
$ pipx install --editable --force . 
```


### 新しいパッケージを作成し、追加

新しいパッケージを作成したら、コマンドのように使用できるようにするため、パッケージをインストールします。
作成したパッケージを、[project.scripts] に追加し、インストールします。

pyproject.toml
```toml
[build-system]
requires = ["setuptools>=61.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "awstools"
version = "0.1.0"
dependencies = [
    "botocore[crt]",
    "boto3",
]
requires-python = ">=3.12"

# ここに追加するコマンド名を追加する。
include = ["sgzu"]

[project.scripts]
# "コマンド名 = モジュール名.ファイル名:関数名"
sgzu = "sgzu.main:main"
```

コマンドとして追加します。
すでにスクリプトが存在するとエラーになるので、--force で強制的に追加します。

```bash
$ pipx install --editable --force . 
```

これ以降は、コマンド名のみでパッケージを実行することができます。

## コマンドの実行

ここにあるツールは、環境変数AWS_ENDPOINT_URLを使用しています。
エミュレータを使用する場合、環境変数AWS_ENDPOINT_URLなどを設定し、でエミュレータの環境設定を行ってください。

このようなシェル関数を作成しておくと、
```
awse() {
  env \
  AWS_ENDPOINT_URL=https://127.0.0.1:9297 \
  AWS_SHARED_CREDENTIALS_FILE="$HOME/.aws/emulator/9297/emulator_credentials" \
  AWS_CONFIG_FILE="$HOME/.aws/emulator/9297/config" \
  AWS_EC2_METADATA_DISABLED=true \
  AWS_DISABLE_HOST_PREFIX_INJECTION=true \
  AWS_REGION=ap-northeast-1 \
  AWS_DEFAULT_REGION=ap-northeast-1 \
  "$@"
}
```

このように実行することでエミュレータ向けとなります。
```
$ awse <ツールのコマンド> <オプション>
# aws cliをエミュレータ向けに実行する。
$ awse aws s3 ls 
```
