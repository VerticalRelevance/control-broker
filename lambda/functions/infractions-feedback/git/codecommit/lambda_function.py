import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import os
from time import time
from collections import ChainMap, OrderedDict

cc = boto3.client('codecommit')
s3 = boto3.client('s3')
ddb = boto3.resource('dynamodb',region_name='us-east-1')

def s3_download(*,Bucket,Key,LocalPath):
    
    try:
        s3.download_file(
            Bucket,
            Key,
            LocalPath
        )
    except ClientError as e:
        print(f'ClientError:\nBucket: {Bucket}\nKey: {Key}\n{e}')
        raise
    else:
        print('No ClientError download_file')
        return True

def query_ddb(*,Table,Pk):
    table = ddb.Table(Table)
    try:
        r = table.query(
            KeyConditionExpression = Key('pk').eq(Pk)
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        print('No ClientError')
        if r['Items']:
            return r['Items']
        else:
            return False
            
class ManageCodeCommit():
    
    def __init__(self,*,
        Repo,
        Branch,
        DescriptionOfChange,
        CfnKey
    ):
        self.repo = Repo
        self.branch = Branch
        self.description_of_change = DescriptionOfChange
        self.cfn_key = CfnKey
        
    def get_latest_commit(self):
        try:
            r = cc.get_branch(
                repositoryName=self.repo,
                branchName=self.branch
            )
        except ClientError as e:
            print(f'ClientError:\n{e}')
            raise
        else:
            parent_commit = r['branch']['commitId']
            self.parent_commit = parent_commit
            return parent_commit

    def new_branch(self,*,NewBranch,CommitId):
        self.new_branch = NewBranch
        try:
            r = cc.create_branch(
                repositoryName=self.repo,
                branchName=self.new_branch,
                commitId=CommitId
            )
        except ClientError as e:
            print(f'ClientError:\n{e}')
            raise
        else:
            print('No ClientError create_branch')
            return True
    
    def put_file_to_new_branch(self,*,FilePath):
        
        with open(FilePath,'rb') as f:
        
            put_file = {
                'filePath': f'cdk.out/{self.cfn_key}',
                'fileMode': 'NORMAL',
                'fileContent': f.read()    
            }
            
        try:
            r = cc.create_commit(
                repositoryName = self.repo,
                branchName = self.new_branch,
                parentCommitId = self.parent_commit,
                authorName = os.environ.get('AWS_LAMBDA_FUNCTION_NAME'),
                commitMessage = self.description_of_change,
                putFiles = [
                    put_file
                ]
            )
        except ClientError as e:
            print(f'ClientError:\n{e}')
            raise
        else:
            print(r)
            new_branch_commit_id = r['commitId']
            return new_branch_commit_id
    
    def create_pr(self):
        try:
            r = cc.create_pull_request(
                title=self.description_of_change,
                description=self.description_of_change,
                targets=[
                    {
                        'repositoryName': self.repo,
                        'sourceReference': self.new_branch,
                        'destinationReference': self.branch
                    },
                ]
            )
        except ClientError as e:
            print(f'ClientError:\n{e}')
            raise
        else:
            print(r)
            pr_id = r['pullRequest']['pullRequestId']
            return pr_id
            
def lambda_handler(event, context):

    print(event)
    now = f'{time():.0f}'
    
    # infractions 
    
    table = event['DynamoDB']['Table']
    pk = event['DynamoDB']['Pk']
    
    query = query_ddb(Table=table,Pk=pk)    
    
    if not query:
        return {
            'InfractionsExist': False
        }
    
    else:
        infractions = [json.loads(i['Infractions']) for i in query]
        print(f'infractions:\n{infractions}')
        # get cfn
        
        cfn_path = '/tmp/cfn.json'
        cfn_key = event['CFN']['Key']
        pr_pk = f'{cfn_key}#{now}'
        
        
        s3_download(
            Bucket = event['CFN']['Bucket'],
            Key = cfn_key,
            LocalPath = cfn_path
        )
        
        # read
        
        with open(cfn_path,'r') as f:
            cfn = json.loads(f.read())
        
        # annotate
        
        before_annotate_keys = list(cfn['Resources'].keys())
        print(f'before_annotate_keys:\n{before_annotate_keys}')
        
        class Annotations():
            
            def __init__(self,*,Resources,Infractions):
                self.resources = Resources
                self.infractions = Infractions
                
                print('infractions:')
                print(Infractions)
                
                self.before_annotate_keys = list(Resources.keys())
            
            def annotate_if_infraction(self,*,Resource):
                
                print(f'Begin annotation.\nResource:\n{Resource}')
                
                key = list(Resource.keys())[0]
                
                infraction = [v for v in infractions if v['resource'] == key]
                
                if infraction:
                    # print('Violation found.')
                    Resource[key]['Violation'] = infraction[0]
                    return Resource
                else:
                    # print('No infraction found.')
                    return Resource
        
            def get_annotated_resources(self):      
                
                annotated_resources = [ self.annotate_if_infraction(Resource={r:self.resources[r]}) for r in self.resources ]
                
                annotated_resources = reversed(annotated_resources)
                
                annotated_resources = dict(ChainMap(*annotated_resources))
            
                return annotated_resources
    
        a = Annotations(
            Resources = cfn['Resources'],
            Infractions = infractions
        )
        
        cfn['Resources'] = a.get_annotated_resources()
        
        after_sorted_keys = list(cfn['Resources'].keys())
        print(f'after_sorted_keys:\n{after_sorted_keys}')
        
        # write
        
        with open(cfn_path, 'w') as f:
            json.dump(cfn, f, indent=2) #line-by-line, not flattened, to improve legibility of diff in PR
        
        # repo
        
        repo = os.environ.get('CdkTsSourceRepo')
        branch = os.environ.get('CdkTsSourceRepoBranch')
        print(f'repo:\n{repo}\nbranch:\n{branch}')
        
        # branch
        
        m = ManageCodeCommit(
            Repo=repo,
            Branch=branch,
            DescriptionOfChange = pr_pk,
            CfnKey = cfn_key
        )
        
        latest_commit = m.get_latest_commit()
        
        m.new_branch(
            NewBranch = pr_pk,
            CommitId = latest_commit
        )
        
        m.put_file_to_new_branch(
            FilePath = cfn_path
        )
        
        m.create_pr()
        
        return {
            'InfractionsExist': bool(infractions)
        }
        
    