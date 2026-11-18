# sgzu/main.py
import sys
import argparse
from sgzu.sg_zu_generator import generate_mermaid_from_sgs

def main():
    parser = argparse.ArgumentParser(description="AWS Security Group to Mermaid ER Converter")
    parser.add_argument("--vpc-id", help="Target VPC ID (e.g., vpc-0123456789abcdef0)", default=None)
    parser.add_argument("--region", help="AWS Region", default="ap-northeast-1")
    
    args = parser.parse_args()

    try:
        # converter.py の関数を呼び出す
        result = generate_mermaid_from_sgs(vpc_id=args.vpc_id, region=args.region)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
