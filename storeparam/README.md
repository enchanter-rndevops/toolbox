# Spring Boot の spring.profiles.active と環境管理を見直してみた

パラメータストアの値をAWS上で直接管理すると、

* パラメータストアの値を大元とした管理がやりづらい。
* パラメータへのコメントがない。
* 修正履歴がない。
* 環境の切り替えがやりづらい

という問題があるように思います。

実際には、パラメータストアではなく環境ごとのプロパティファイルだけで運用することもできます。しかし、Spring Boot では Spring Profile ごとに読み込む設定ファイルが変わるため、環境の追加や運用方法によっては設定の管理が複雑になります。

それらの問題を解決するため、パラメータストアの値をgit上で管理し、スクリプトでパラメータストアに投入する方式としてみました。

このスクリプトでは、以下のような形式で管理することを前提としています。

```
/project-name/application-name/env/<パラメータ名>
```

パラメータストアの値となるファイルは、ただのプロパティファイルなので、gitで管理できます。
投入スクリプトの引数を変更するだけで新しいパラメータストアができます。

Spring Profile は aws や local などの実行方式を表すために使用します。
dev、stg、prod といったデプロイ環境の切り替えには使用しません。

環境の切り替えには ENV 環境変数を利用し、Parameter Store の参照先のみを変更します。

## パラメータの値を管理

### 環境別のプロパティファイルを作成

parameterstore-\<env\>.properties ファイルを作成します。
内容は普通のプロパティファイルです。

### パラメータストアに値を投入

pipx でインストールしておきます。

```bash
$ storeparam -prefix=<project-name>/<application-name> -env=<env>
```

パラメータストア名は、以下の通りになります。

```
<パラメータprefixの値>/<パラメータenvの値>/<投入するプロパティ名>
```

### アプリケーションのプロパティファイル

SpringBootを使うことを前提としています。

プロパティファイル application-<SPRING_PROFILES_ACTIVE>.properties を作成します。

作成したプロパティファイルに以下の設定を追加します。
application-<SPRING_PROFILES_ACTIVE>.properties
```properties
spring.config.import=aws-parameterstore:<project-name>/<application-name>/${ENV}/,aws-secretsmanager:<project-name>/<application-name>/${ENV}/
```

spring.config.import で storeparam で設定したパラメータストアの値が読み込まれます（同時にシークレットマネージャーの値も読み込まれます）。


ローカル(application-local.properties)では直接プロパティファイルで設定し、シークレットマネージャーの値だけspring.config.importを使用して読み込むのがいいと思います。

パラメータストアにのみ設定がある状態にしておくと、設定があるところをまとめることができるので、application.propertiesは空にしておくといいと思います。

## さいごに

とあるプロジェクトで、Spring の spring.profiles.activeの値からプロパティファイルを読み込むようになっていました。
spring.profiles.active の設定が Tomcat の conf 配下で行われており、どこで設定されているのか探すのに苦労したり。
複数あるdev環境にデプロイするときに、EC2インスタンスに接続し、viでプロパティファイルを変更する必要がある。
プロパティファイルにRDSのパスワード。OAuth2のキーがある（gitlabにコミットしてあったのは見なかったことにしたい）。
とか、それはそれはツッコミどころという点では枚挙にいとまがないというか。ネタが尽きないというか。おもしろい現場があったわけです。

これらを解決するため、プロパティの設定をどうするかを見直してみました。

結局、これが日の目を見ることはありません（なので、この方式も実務で使ったことはありません）でしたが、このようにまとめるきっかけになったという意味ではいい現場だったのかなと思います。
