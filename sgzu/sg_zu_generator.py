# my_cli/sg_zu_generator.py
import boto3
import re

def sanitize_name(name: str) -> str:
    """Mermaidの識別子として使えるように記号をアンダースコアに置換"""
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

def format_port(rule: dict) -> str:
    """プロトコルとポート範囲を整形"""
    proto = rule.get('IpProtocol', '-1')
    if proto == '-1':
        return 'ALL'
    
    from_p = rule.get('FromPort')
    to_p = rule.get('ToPort')
    
    if from_p is None:
        return proto.upper()
    if from_p == to_p:
        return f"{proto.upper()}_{from_p}"
    return f"{proto.upper()}_{from_p}-{to_p}"

def generate_mermaid_from_sgs(vpc_id: str = None, region: str = 'ap-northeast-1') -> str:
    """セキュリティグループを取得し、IN/OUTをセクション分けしたクラス図（Mermaid）を返す"""
    ec2 = boto3.client('ec2', region_name=region)
    
    filters = [{'Name': 'vpc-id', 'Values': [vpc_id]}] if vpc_id else []
    response = ec2.describe_security_groups(Filters=filters)
    sgs = response.get('SecurityGroups', [])

    sg_id_to_name = {}
    for sg in sgs:
        name_tag = next((t['Value'] for t in sg.get('Tags', []) if t['Key'] == 'Name'), None)
        display_name = name_tag if name_tag else sg['GroupName']
        sg_id_to_name[sg['GroupId']] = sanitize_name(display_name)

    lines = ["```mermaid", "classDiagram"]
    
    class_contents = []
    relations = []

    for sg in sgs:
        sg_id = sg['GroupId']
        sg_name = sg_id_to_name[sg_id]
        
        class_contents.append(f"    class {sg_name} {{")
        class_contents.append(f"        ID:{sg_id}")
        class_contents.append(f"        --")
        class_contents.append(f"        [Inbound]")

        # インバウンドルール用のリスト
        ingress_lines = []
        # アウトバウンドルール用のリスト
        egress_lines = []

        # --- 1. インバウンドルール (Ingress) の収集 ---
        for perm in sg.get('IpPermissions', []):
            port_info = format_port(perm)

            for ip_range in perm.get('IpRanges', []):
                cidr = ip_range['CidrIp']
                safe_cidr = sanitize_name(cidr)
                #ingress_lines.append(f"        IN_{port_info}_{safe_cidr} \"{cidr}\"")
                ingress_lines.append(f"        IN {port_info} {cidr}")

            for ipv6_range in perm.get('Ipv6Ranges', []):
                cidr_v6 = ipv6_range.get('CidrIpv6')
                if cidr_v6:
                    safe_v6 = sanitize_name(cidr_v6)
                    #ingress_lines.append(f"        IN_{port_info}_{safe_v6} \"{cidr_v6}\"")
                    ingress_lines.append(f"        IN {port_info} {cidr_v6}")

            for pl in perm.get('PrefixListIds', []):
                pl_id = pl['PrefixListId']
                #ingress_lines.append(f"        IN_PL_{port_info}_{pl_id} \"{pl_id}\"")
                ingress_lines.append(f"        IN_PL {port_info} {pl_id}")

            for pair in perm.get('UserIdGroupPairs', []):
                src_sg_id = pair['GroupId']
                src_sg_name = sg_id_to_name.get(src_sg_id, sanitize_name(src_sg_id))
                desc = pair.get('Description', '')
                label = f"{port_info}" + (f" ({desc})" if desc else "")

                ingress_lines.append(f"        IN_SG {port_info} {src_sg_name}")

                relations.append(f"    {src_sg_name} --> {sg_name} : {label}")

        # --- 2. アウトバウンドルール (Egress) の収集 ---
        for perm in sg.get('IpPermissionsEgress', []):
            port_info = format_port(perm)

            for ip_range in perm.get('IpRanges', []):
                cidr = ip_range['CidrIp']
                safe_cidr = sanitize_name(cidr)
                #egress_lines.append(f"        OUT_{port_info}_{safe_cidr} \"{cidr}\"")
                egress_lines.append(f"        OUT {port_info} {cidr}")

            for ipv6_range in perm.get('Ipv6Ranges', []):
                cidr_v6 = ipv6_range.get('CidrIpv6')
                if cidr_v6:
                    safe_v6 = sanitize_name(cidr_v6)
                    #egress_lines.append(f"        OUT_{port_info}_{safe_v6} \"{cidr_v6}\"")
                    egress_lines.append(f"        OUT {port_info} {cidr_v6}")

            for pl in perm.get('PrefixListIds', []):
                pl_id = pl['PrefixListId']
                egress_lines.append(f"        OUT_PL_{port_info}_{pl_id} \"{pl_id}\"")

            for pair in perm.get('UserIdGroupPairs', []):
                dst_sg_id = pair['GroupId']
                dst_sg_name = sg_id_to_name.get(dst_sg_id, sanitize_name(dst_sg_id))
                desc = pair.get('Description', '')
                label = f"{port_info}" + (f" ({desc})" if desc else "")

                egress_lines.append(f"        OUT_SG {port_info} {dst_sg_name}")

                relations.append(f"    {sg_name} --> {dst_sg_name} : {label}")

        # ルールが空の場合のプレースホルダー
        # if not ingress_lines:
        #     ingress_lines.append("        (none)")
        # if not egress_lines:
        #     egress_lines.append("        (none)")

        # クラス内にインバウンドルールを追加
        class_contents.extend(ingress_lines)
        
        # インバウンドとアウトバウンドを分ける2つ目の仕切り線
        class_contents.append("        --")
        class_contents.append(f"        [Outbound]")
        
        # クラス内にアウトバウンドルールを追加
        class_contents.extend(egress_lines)

        class_contents.append("    }")

    lines.extend(class_contents)
    lines.append("")
    for rel in sorted(set(relations)):
        lines.append(rel)

    lines.append("```")
    return "\n".join(lines)