# AWSのセキュリティグループを可視化して設定確認を楽にする

セキュリティグループの関係を、実際の AWS 環境から設定を取得して Mermaid 図として出力するツールを作成しました。

コマンド名はsgzuで、お察しの通り、

sg = セキュリティグループ
zu = 図

です。覚えやすいですね。覚えていってください。

できること

* セキュリティグループ間の許可関係を可視化
* インバウンド / アウトバウンドルールを一覧表示
* Mermaid ダイアグラムとして出力

## なぜこれを作成したのか

AWS コンソールでは、セキュリティグループは一覧形式で表示されます。

セキュリティグループの設定ミスを調査したり、構築された環境が設計どおりになっているか確認したりする場合、この作業は非常に手間がかかります。
つまり、こういうことになるわけですね。

リソースからセキュリティグループを見る
→ セキュリティグループの設定を表示する
→ リソースによって表示のしかたが違うのにキレる
→ 通信先、元のセキュリティグループを表示する
→ まちがってセキュリティルールIDを見てしまう
→ ブラウザのタブが増える
→ どのタブでなにを表示していたのかわからなくなる
→ 余分なタブを閉じる
→ 余分でないタブも閉じてしまう
→ 最初に戻る

このような無駄な作業を減らすために、このツールを作成しました。

コードはAIが生成したものを利用目的に合わせて修正したものです。
設計上の方針として、

- セキュリティグループを主体とする
- リソースは表示しない
- インバウンドルールを元に通信関係を可視化する
- 図が複雑になりすぎるためアウトバウンド矢印は出力しない

としています。

## インストール

[TOOLBOX](https://github.com/enchanter-rndevops/toolbox) から git clone でソースを取得。
pipxで TOOLBOX をインストールすると、sgzuがインストールされます。

## 使う

aws にログイン

```
$ aws login
```

図を生成
生成結果は標準出力に出力されます。
適当なファイルへリダイレクトし、Markdownファイルへコピーしてください。

```
$ sgzu 
```mermaid
classDiagram
    class ECS_Backend_1 {
        ID:sg-0bf9fbba39c6bb531
        --
        [Inbound]
        IN_SG TCP_8080 ALB_1
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }
    class EC2_Fumidai_1 {
        ID:sg-07b12054c934c7c37
        --
        [Inbound]
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }
    class ALB_1 {
        ID:sg-005c325c0cd27574c
        --
        [Inbound]
        IN_PL TCP_80 pl-58a04531
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }
    class RDS_1 {
        ID:sg-0f515231be4149acb
        --
        [Inbound]
        IN_SG TCP_3306 EC2_Fumidai_1
        IN_SG TCP_3306 ECS_Backend_1
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }
    class VPC_Endpoint {
        ID:sg-08efde632649ad74b
        --
        [Inbound]
        IN TCP_443 172.31.0.0/16
        IN TCP_443 406:da14:1959:3200::/56
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }
    class default {
        ID:sg-06772d03b010392cd
        --
        [Inbound]
        IN_SG ALL default
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }

    ALB_1 --> ECS_Backend_1 : TCP_8080
    EC2_Fumidai_1 --> RDS_1 : TCP_3306
    ECS_Backend_1 --> RDS_1 : TCP_3306
    default --> default : ALL
```

## 読み方

このツールが出力するのはセキュリティグループのみです。
EC2、ALB、ECS、RDSなどのリソースは出力されません。

ボックスの見出しはセキュリティグループ名です。
セキュリティグループIDとインバウンド、アウトバウンドをすべて表示しています。

矢印はインバウンド設定をもとに書いています。アウトバウンドの設定によっては、矢印があっても実際に通信が通らない場合があります。

```mermaid
classDiagram
    class ECS_Backend_1 {
        ID:sg-0bf9fbba39c6bb531
        --
        [Inbound]
        IN_SG TCP_8080 ALB_1
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }
    class EC2_Fumidai_1 {
        ID:sg-07b12054c934c7c37
        --
        [Inbound]
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }
    class ALB_1 {
        ID:sg-005c325c0cd27574c
        --
        [Inbound]
        IN_PL TCP_80 pl-58a04531
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }
    class RDS_1 {
        ID:sg-0f515231be4149acb
        --
        [Inbound]
        IN_SG TCP_3306 EC2_Fumidai_1
        IN_SG TCP_3306 ECS_Backend_1
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }
    class VPC_Endpoint {
        ID:sg-08efde632649ad74b
        --
        [Inbound]
        IN TCP_443 172.31.0.0/16
        IN TCP_443 406:da14:1959:3200::/56
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }
    class default {
        ID:sg-06772d03b010392cd
        --
        [Inbound]
        IN_SG ALL default
        --
        [Outbound]
        OUT ALL 0.0.0.0/0
        OUT ALL ::/0
    }

    ALB_1 --> ECS_Backend_1 : TCP_8080
    EC2_Fumidai_1 --> RDS_1 : TCP_3306
    ECS_Backend_1 --> RDS_1 : TCP_3306
    default --> default : ALL
```

## さいごに 

セキュリティグループの設定確認や設計レビューの際に、AWS コンソールを何往復もする代わりに sgzu を使って全体像を確認できるようになりました。

同じ悩みを持っている方の参考になれば幸いです。
