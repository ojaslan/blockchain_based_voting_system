import streamlit as st
import hashlib
import json
import time

# Blockchain Class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.voters = set()
        self.load_data()
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self):
        """Creates the first block in the blockchain."""
        genesis_block = {
            "index": 1,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "votes": {},
            "previous_hash": "0",
            "hash": self.hash_block({}, "0"),
        }
        self.chain.append(genesis_block)
        self.save_data()

    def create_block(self, votes, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "votes": votes,
            "previous_hash": previous_hash,
            "hash": self.hash_block(votes, previous_hash),
        }
        self.chain.append(block)
        self.save_data()
        return block

    def hash_block(self, votes, previous_hash):
        block_string = json.dumps(votes, sort_keys=True) + previous_hash
        return hashlib.sha256(block_string.encode()).hexdigest()

    def get_latest_block(self):
        return self.chain[-1] if self.chain else None

    def save_data(self):
        with open("votes.json", "w") as f:
            json.dump({"chain": self.chain, "voters": list(self.voters)}, f, indent=4)

    def load_data(self):
        try:
            with open("votes.json", "r") as f:
                data = json.load(f)
                self.chain = data.get("chain", [])
                self.voters = set(data.get("voters", []))
        except FileNotFoundError:
            self.chain = []
            self.voters = set()

# Initialize Blockchain
blockchain = Blockchain()

# Set page config
st.set_page_config(page_title="Blockchain Voting", page_icon="🗳", layout="wide")

st.markdown("<h1>🗳 Secure Blockchain-Based Voting System</h1>", unsafe_allow_html=True)

# Sidebar for Voter Input
st.sidebar.header("🔐 Voter Authentication")
voter_id = st.sidebar.text_input("🔑 Enter your Unique Voter ID:", max_chars=10)

# Hash the voter ID for security
def hash_voter_id(voter_id):
    return hashlib.sha256(voter_id.encode()).hexdigest()

# Candidate Selection
st.sidebar.header("🗳 Vote Now")
candidates = ["BJP", "Shiv Sena", "NCP", "NOTA"]
selected_candidate = st.sidebar.radio("Select your candidate:", candidates)

# Voting Button
if st.sidebar.button("✅ Submit Vote"):
    if not voter_id:
        st.sidebar.warning("⚠ Please enter a valid Voter ID!")
    else:
        voter_hash = hash_voter_id(voter_id)  # Hash voter ID
        if voter_hash in blockchain.voters:
            st.sidebar.error("❌ You have already voted!")
        else:
            last_block = blockchain.get_latest_block()
            new_votes = last_block["votes"].copy() if last_block else {}

            new_votes[selected_candidate] = new_votes.get(selected_candidate, 0) + 1
            blockchain.create_block(new_votes, last_block["hash"] if last_block else "0")
            blockchain.voters.add(voter_hash)  # Store hashed ID
            blockchain.save_data()

            st.sidebar.success(f"✅ Vote cast for {selected_candidate}!")

# Display Vote Count
st.markdown("<h2 style='text-align: center; color:#ffcc00;'>📊 Live Vote Count</h2>", unsafe_allow_html=True)
latest_block = blockchain.get_latest_block()

if latest_block:
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        vote_data = latest_block["votes"]

        col1.metric(label="🔹 BJP", value=vote_data.get("BJP", 0))
        col2.metric(label="🔹 Shiv Sena", value=vote_data.get("Shiv Sena", 0))
        col3.metric(label="🔹 NCP", value=vote_data.get("NCP", 0))
        col4.metric(label="🔹 NOTA", value=vote_data.get("NOTA", 0))

# Show Blockchain Data
if st.checkbox("📜 View Blockchain Data"):
    st.json(blockchain.chain)
