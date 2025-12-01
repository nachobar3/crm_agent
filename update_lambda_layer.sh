#!/bin/bash
# Script to create and update Lambda Layer with dependencies

echo "📦 Creating Lambda Layer with dependencies..."

# Create temporary directory
mkdir -p lambda_layer/python

# Install dependencies to the layer directory
pip install -r requirements.txt -t lambda_layer/python/

# Create zip file
cd lambda_layer
zip -r ../lambda_layer.zip python/
cd ..

echo "✅ Lambda layer package created: lambda_layer.zip"
echo ""
echo "📤 To update your Lambda Layer, run:"
echo "aws lambda publish-layer-version \\"
echo "  --layer-name your-layer-name \\"
echo "  --zip-file fileb://lambda_layer.zip \\"
echo "  --compatible-runtimes python3.11 python3.12 \\"
echo "  --region your-region"
echo ""
echo "Then update your Lambda function to use the new layer version"

# Cleanup
rm -rf lambda_layer

