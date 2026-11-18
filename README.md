# TOOLBOX

開発に使用するpython便利スクリプトをまとめているプロジェクト。

スクリプトのリスト

* **[sgzu](./sgzu/README.md)**
  セキュリティグループの図(mermaidダイアグラム)を自動生成する。

## ツールを使う

pyenvとpipxを使用し、コマンドのように使えるようにします。

### Pythonのインストール

aptではなく、pyenvを使用します。
システムのPythonでよければ、pyenvでpythonをインストールする必要はありません。

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

pipxを使うことで、venvの設定を自動的に行い、コマンド名でスクリプトを実行することができます。
ここでは行いませんが、使用するpythonのバージョンを変更することもできます。

### pipxのインストール

```bash
$ sudo apt update && sudo apt install pipx -y
```

### 新しいパッケージを追加

新しいパッケージを作成したら、コマンドのように使用できるようにするため、パッケージをインストールします。
作成したパッケージを、[project.scripts] に追加する。

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
