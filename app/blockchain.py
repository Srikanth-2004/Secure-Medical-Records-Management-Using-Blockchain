import hashlib
import json
from time import time
from datetime import datetime

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash='1', proof=100)  # Genesis block

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.now()),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []  # Reset the current list of transactions
        self.chain.append(block)
        return block

    def new_transaction(self, action, doctor_id=None, patient_id=None, user_id=None):
        """
        Creates a new transaction to go into the next mined block.

        :param action: Action performed (e.g., "login", "access_requested").
        :param doctor_id: ID of the doctor (optional).
        :param patient_id: ID of the patient (optional).
        :param user_id: ID of the user (optional).
        :return: The index of the block that will hold this transaction.
        """
        self.current_transactions.append({
            'doctor_id': doctor_id,
            'patient_id': patient_id,
            'user_id': user_id,
            'action': action,
            'timestamp': str(datetime.now()),
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"