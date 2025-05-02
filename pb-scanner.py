import sys
import requests
import json
import time
import re

import argparse

def main():
        argParser = argparse.ArgumentParser()
        argParser.add_argument("-u", "--url", type=ascii, help="base URL for PB", required=True)
        argParser.add_argument("-c", "--cookie", type=ascii, help="JSESSIONID value to use")
        argParser.add_argument("-l", "--log", help="log output to a file",  action="store_true")
        argParser.add_argument("-v", "--verbose", help="verbose output",  action="store_true")
        args = argParser.parse_args()

        #pbRoot = input('Enter the base URL for PB (ex: https://school.edu/BannerExtensibility): ');
        pbRoot = args.url.replace("'", "")
        pbPageUrl = '/internalPb/virtualDomains.pbadmListPages';
        nonPbPageUrl = '/internalPb/virtualDomains.pbadmNonAdmPages';
        pageRoot = '/customPage/page/';
        
        if(args.cookie is not None):
                cookie = args.cookie.replace("'", "")

        accessiblePages = list();
        inaccessiblePages = list();

        #print("Starting scan of host " + pbRoot);
        #print("Using URL " + pbRoot + pbPageUrl);

        ## test the root
        pbPageList = requests.get(pbRoot + pbPageUrl);
        pbPageListJson = pbPageList.json();

        pageCount = len(pbPageListJson);
        print("DEBUG: pageCount: " + str(pageCount));

        for page in pbPageListJson:
                pageName = page['CONSTANT_NAME'];
                pageUrl = pbRoot + pageRoot + pageName;
                #print("DEBUG: url: " + pageUrl);
                if(args.cookie is not None):
                    #print("DEBUG: using JSESSIONID: " + cookie);
                    cookie_jar = {'JSESSIONID': cookie}
                    pageTest = requests.get(pageUrl, cookies=cookie_jar, allow_redirects=False);
                else:
                    #print("DEBUG: running unauthenticated");
                    pageTest = requests.get(pageUrl, allow_redirects=False);
                #print("DEBUG: pageTest.status_code: " + str(pageTest.status_code));
                if pageTest.status_code == 200:
                        #print("page (" + pageName + ") is accessible");
                        print('.', end='', flush=True)
                        # let's check the response for domains: pbResource('virtualDomains.exampleDomain');
                        # regexp = "pbResource\(\'(.*)\'\)"gm
                        domainList = re.findall("pbResource\(\'(.*)\'\)", pageTest.text);
                        if(domainList):
                                #print("DEBUG: pageName: " + " domainList: " + str(domainList));
                                testdict = { 'name': pageName, 'url': pageUrl, 'domains': str(domainList) };
                                ##  foreach domain we should check the next instance of queryParams
                                ##  queryParams: '{p_id : $scope.BlockSearchStudent_InputID}',
                                ##  /queryParams: '{(.*)}'/gm
                        else:
                                testdict = { 'name': pageName, 'url': pageUrl, 'domains': 'none' };
                        accessiblePages.append(testdict);
                else:
                        #print("page (" + pageName + ") is NOT accessible");
                        print('.', end='', flush=True)
                        inaccessiblePages.append(pageUrl);
                #time.sleep(1)

        print("");  # empty line for formatting
        print("----------------------------------");
        print("Summary Report");
        accessibleCount = len(accessiblePages);
        print("Accessible count: " + str(accessibleCount));

        percentageAccessible = (accessibleCount / pageCount)*100;
        print("Percentage accessible = " + str(percentageAccessible));
        print("----------------------------------");

        print("Listing accessible pages, URLs and associated domains:");
        for page in accessiblePages:
          print(page);
          #print("domains for " + x['name']);
          #print(x['name']);

if __name__ == '__main__':
    main()
