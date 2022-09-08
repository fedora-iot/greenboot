#!/bin/bash
set -e

REPOS_DIRECTORY=/etc/ostree/remotes.d
DOMAINS_WITH_PROBLEMS=()

get_domain_names_from_platform_urls() {
    DOMAIN_NAMES=$(grep -P -ho 'http[s]?\:\/\/[a-zA-Z0-9./-]+' $REPOS_DIRECTORY/* \
        | grep -v -P '.*[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' \
        | awk -F:// '{print $2}' \
        | awk -F/ 'BEGIN{OFS="\n"}{print $1}' \
        | sort | uniq)
    if [[ -z $DOMAIN_NAMES ]]; then
        echo "No domain names have been found"
    fi
}

get_dns_resolution_from_domain_names() {
    # Check if each domain name resolve into at least 1 IP
    # If it doesn't, add it to DOMAINS_WITH_PROBLEMS
    for line in $DOMAIN_NAMES; do
        NUMBER_OF_IPS_PER_DOMAIN=$(getent hosts "$line" | wc -l)
        if [[ $NUMBER_OF_IPS_PER_DOMAIN -eq 0 ]]; then
            DOMAINS_WITH_PROBLEMS+=( "$line" )
        fi
    done
}

assert_dns_resolution_result() {
    # If the number of domains with problems is 0, everything's good
    # If it's not 0, we exit with errors and print the domains
    if [[ ${#DOMAINS_WITH_PROBLEMS[@]} -eq 0 ]]; then
        echo "All domains have resolved correctly"
        exit 0
    else
        echo "The following repository domains haven't responded properly to DNS queries:"
        echo "${DOMAINS_WITH_PROBLEMS[*]}"
        exit 1
    fi
}

if [[ ! -d $REPOS_DIRECTORY ]]; then
    echo "${REPOS_DIRECTORY} doesn't exist"
    exit 1
fi

if [ -z "$(ls -A $REPOS_DIRECTORY)" ]; then
   echo "${REPOS_DIRECTORY} is empty, skipping check"
   exit 0
fi

get_domain_names_from_platform_urls
if [[ -n $DOMAIN_NAMES ]]; then
    get_dns_resolution_from_domain_names
    assert_dns_resolution_result
fi
