#!/bin/bash
# Run Bolton comprehensive tests
SITE=${1:-$(ls ../../../sites/ | grep -v assets | grep -v apps.txt | head -1)}
echo "Running Bolton tests on site: $SITE"
cd /home/erpnext/frappe-bench
bench --site $SITE run-tests --app bolton --module bolton.ruleflow.tests.test_comprehensive -v
