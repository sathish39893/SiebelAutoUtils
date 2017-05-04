'''
Created on May 4, 2017

@author: sathish
'''
import re
dateValue="10/4/9999";
result=re.search("^([1-9]|[12][0-9]|3[01])/(\d|1[012])/\d(\d?){3}$", dateValue);
print(str(result))



