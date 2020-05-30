from django.core.exceptions import ValidationError
import ipaddress

def validate_ips(self):

    ip_list = self

    print(ip_list)

    ip_list = ip_list.split(',')

    for ip in ip_list:

        ip = ip.split('.')

        if len(ip) != 4:

            raise ValidationError("Submitted an incorrect IP address")

        for num in ip:

            print(num)
            
            if num.isdigit():

                i = int(num)

                if i < 0 or i > 255:

                    raise ValidationError("One of the fields is not in the IP range")

            else:

                #TODO: Extra validation of the IP ranges submitted
                if '/' or '-' in num:

                    pass
                    
                else:

                    raise ValidationError("One of the fields is not a number")








