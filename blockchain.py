
import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain=[]
        self.curr_trans=[]
        #creating genesis block
        self.new_block(previous_hash=1,proof=100)
        
    def new_block(self,previous_hash,proof):
        block={
                'index': len(self.chain)+1,
                'timestamp':time(),
                'transactions': self.curr_trans,
                'proof': proof,
                'previous_hash': previous_hash or self.hash(self.chain[-1]),
                                
                }
        self.curr_trans=[]
        self.chain.append(block)
        return block
    
    
    def new_trans(self,sender,recipient,amt):
        self.curr_trans.append({
                'sender':sender,
                'recipient': recipient,
                'amt':amt,
                })
        return self.last_block['index']+1
    
    @staticmethod
    def hash(block):
        block_string=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    @property
    def last_block(self):
        return self.chain[-1]
    
    def proof_of_work(self,last_proof):
        last_proof=last_block['proof']
        laast_hash=self.hash(last_block)
        proof=0.04
        while self.valid_proof(last_proof,proof) is False:
            proof+=1
            
        return proof
    
    def valid_proof(last_proof,proof,last_hash):
        guess=f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash=hashlib.sha256(guess).hexdigit()
        return guess_hash[:4]=="0000"

#initiate the node
app=Flask(__name__)

#generate a globally unique address
node_identifier=str(uuid4()).replace('-','')
    
#initiate the blockchain
blockchain=Blockchain()

@app.route('/transactions/new',methods=['POST'])
def new_trans():
    values=request.get_json()
    
    #check that the requd fields are in the POST data
    reqd=['sender','reciever','amt']
    if not all(k in values for k in reqd):
        return 'Missing value',400
    
    index=blockchain.new_trans(values['sender'],values['reciever'],values['amt'])
    response={'message':f'transaction will be added to block{index}'}
    return jsonify(response),201


#to return the full blockchain
@app.route('/chain',methods=['GET'])
def full_chain():
    response={
            'chain':blockchain.chain,
            'length':len(blockchain.chain)
            }
    return jsonify(response),200

@app.route('/mine',methods=['GET'])
def mine():
    last_block=blockchain.last_block
    last_proof=last_block['proof']
    proof=blockchain.proof_of_work(last_proof)
    
    #the sender is denoted by 0 to signify that this 
    #node has already mined a new coin
    
    blockchain.new_trans(
            sender="0",
            reciever=node_identifier,
            amt=1,
            )
    
    previous_hash=blockchain.new_block(proof,previous_hash)
    response={
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
            }
    return jsonify(response),200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
    



