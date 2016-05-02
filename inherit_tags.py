import boto3

session = boto3.Session(profile_name='myprofile')
account_id = session.resource('iam').CurrentUser().arn.split(':')[4]

ec2 = session.resource('ec2', region_name='us-west-2')
##ec2 = session.resource('ec2', region_name='ap-southeast-2')

target_tag='Purpose'
DEBUG=False

def check_for_tag(tags, target_tag):
    if tags is None:
        #print "no tags"
        return False
    else:
        for tag in tags:
            if tag['Key']==target_tag:
                return tag['Value']
        return False 
  
def tags2dict(tags):
    tagsdict={}
    if not tags is None:
        for tag in tags:
            tagsdict[tag['Key']]=tag['Value']
        return tagsdict
    else:
        return False

def process(instances):
    volumes=ec2.volumes.all()
    snapshots=ec2.snapshots.filter(OwnerIds=[account_id])
    nics=ec2.network_interfaces.all()
    
    for i in instances:
        print i.id
        tag_value=check_for_tag(i.tags,target_tag)
        if not tag_value:
            print 'no tags'
        else:
            for v in volumes:
                if v.attachments[0]['InstanceId']==i.id: 
                    print "{0} / {1}".format(i.id,v.id),
                    if not check_for_tag(v.tags,target_tag)==tag_value:
                        print 'tagging volume'
                        if not DEBUG:
                            v.create_tags(Tags=[{ 'Key': target_tag, 'Value': tag_value},])
                    else :
                        print tag_value
                    for s in snapshots:
                        if s.volume_id==v.id: 
                            print '{0} / {1} / {2}'.format(i.id, v.id, s.id),
                            if not check_for_tag(s.tags,target_tag)==tag_value:
                                print 'tagging snapshot'
                                if not DEBUG: 
                                    s.create_tags(Tags=[{ 'Key': target_tag, 'Value': tag_value},])
                            else:
                                print tag_value

            for n in nics:
                if n.attachment['InstanceId']==i.id:
                    print "{0} / {1}".format(i.id,n.id),
                    if not check_for_tag(n.tag_set,target_tag)==tag_value:
                        print 'tagging nic'
                        if not DEBUG:
                            n.create_tags(Tags=[{ 'Key': target_tag, 'Value': tag_value},])
                    else:
                        print tag_value
                
                



def main():
#    process(ec2.instances.filter(InstanceIds=['i-nnnnnnn']))
    process(ec2.instances.all())
    

if __name__ == "__main__":
    main()
