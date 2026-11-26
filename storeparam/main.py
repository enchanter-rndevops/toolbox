import boto3
import os
import sys
import argparse

parser = argparse.ArgumentParser(
    description="Export AWS Systems Manager Parameter Store to properties file",
    usage="%(prog)s --prefix <project-name>/<application-name> --env <env>"
    )
parser.add_argument("--prefix", required=True)
parser.add_argument("--env", required=True, choices=["dev", "stg", "prod"])

args = parser.parse_args()

PREFIX = f"{args.prefix}/{args.env}/"
PROPERTIES_FILE = f"parameterstore-{args.env}.properties"

# ================================
# properties ファイル読み込み
# ================================
def load_properties(path):
    props = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    print(f"⚠️ 無効な行をスキップ: {line}")
                    continue
                key, value = line.split("=", 1)
                props[key.strip()] = value.strip()
        return props
    except FileNotFoundError:
        print(f"❗ properties ファイルが存在しません: {path}")
        sys.exit(1)

# ================================
# SecureString 判定
# ================================
def is_secure_key(key: str) -> bool:
    """
    spring.datasource.password など、
    パスワード・秘密鍵・トークン系は SecureString にする。
    """
    secure_keywords = ["password", "secret", "token", "key"]
    return any(k in key.lower() for k in secure_keywords)


# ================================
# Parameter Store へ投入
# ================================
def put_parameter(name: str, value: str, secure: bool):
    ssm = boto3.client("ssm")

    param_type = "SecureString" if secure else "String"

    try:
        ssm.put_parameter(
            Name=name,
            Value=value,
            Type=param_type,
            Overwrite=True
        )
        print(f"🆗 パラメータストアに登録しました {name} ({param_type}) ")
    except Exception as e:
        print(f"⚠️ パラメータストアの登録に失敗しました {name} {e}")
        sys.exit(1)


# ================================
# メイン処理
# ================================
def main():
    print("ℹ️ Parameter Store の更新を開始します。")
    print("env       :", {args.env})
    print("prefix    :", PREFIX)
    print("properties:", PROPERTIES_FILE)

    props = load_properties(PROPERTIES_FILE)

    if not props:
        print("❗ properties が空です")
        sys.exit(1)

    for key, value in props.items():
        full_name = PREFIX + key  # spring.datasource.url のような .区切りのまま
        secure = is_secure_key(key)
        put_parameter(full_name, value, secure)

    print("🆗 Parameter Store を更新しました。")


if __name__ == "__main__":
    main()
