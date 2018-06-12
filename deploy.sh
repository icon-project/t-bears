[[ -z "$1" ]] && { echo "Version should be not empty" ; exit 1; }

pip install awscli

export  AWS_ACCESS_KEY_ID=AKIAJYKHNVJS4GYQTV2Q
export AWS_SECRET_ACCESS_KEY=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

aws s3 cp $1 s3://unchain.icon.foundation --recursive --acl public-read