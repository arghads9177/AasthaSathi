# Cobank API Documentation

Base URL:  
`https://web.myaastha.in/cobankapi/api`

Authentication (Required for all endpoints):
> Replace `<your-token>` with a valid issued token.

---

## 1️⃣ Branch API

### POST /branch/search
**Purpose:** Search branches  
**Request Body Fields** (all optional)
- bcode: string  
- name: string  
- address: string  
- city: string  
- pin: string  
- obalance: float  
- obalanceon: date (YYYY-MM-DD)  
- status: string [Active, Inactive]  
- ocode: string  

**Response:** JSON array  
**Errors:** 400 / 401 / 500  

---

## 2️⃣ Deposit Scheme API

### POST /depositscheme/search
**Purpose:** Search deposit schemes  
**Request Body Fields:**
- actype: string [SB, RD, FD, MIS]
- name: string
- tenure: float
- tunit: string [Year, Month]
- interestrate: float
- lastchangedon: date
- minbalance: float (only SB)
- mindeposit: float
- maxdeposit: float
- status: string [Running, Closed]
- prematurityslab: array ({tenure: int, irate: float})
- ocode: string

**Response:** JSON array  
**Errors:** 400 / 401 / 500  

---

## 3️⃣ Loan Scheme API

### POST /loanscheme/search
**Purpose:** Search loan schemes  
**Request Body Fields:**
- name: string
- category: string [Secured, Unsecured]
- tenure: int (months)
- interesttype: string [Flat, Reducing]
- interestrate: float
- lastchangedon: date
- minamount: float
- maxamount: float
- status: string [Running, Closed]
- ocode: string

**Response:** JSON array  
**Errors:** 400 / 401 / 500  

---

## 4️⃣ Member APIs

### POST /member/search
**Purpose:** Search members  
**Request Body Fields:**
- memberno: int
- applicaionno: string
- name: string
- fhname: string
- gender: string
- caste: string [General, SC, ST, OBC]
- bdate: date
- address: string
- city: string
- pin: string
- district: string
- paddress: string
- pcity: string
- ppin: string
- pdistrict: string
- nominee: string
- relation: string
- naddress: string
- pan: string
- dlno: string
- voterno: string
- aadhar: string
- otheridentity: string
- image: string
- signature: string
- identityimage: string
- panimage: string
- addressproofimage: string
- status: string [New, Member, Canceled]
- mtype: string [Share, Nominal]
- createdon: date
- canceledon: date
- reason: string
- mobile: string
- email: string
- membership: string [Single, Joint]
- premium: boolean
- ocode: string

**Response:** JSON array  
**Errors:** 400 / 401 / 500  

---

### POST /member/searchCount
**Purpose:** Count members  
**Request:** Same fields as /member/search  
**Response:** number  
**Errors:** 400 / 401 / 500  

---

## 5️⃣ Account APIs

### POST /account/search
**Purpose:** Search accounts  
**Request Body Fields:**
- applicationno: string
- memberno: string
- accountno: string
- actype: string [SB, RD, FD, MIS]
- sname: string
- appliedon: date
- createdon: date
- maturedon: date
- closedon: date
- fvalue: float
- dvalue: float
- wvalue: float
- irate: float
- interest: float
- mvalue: float
- status: string [Applied, New, Running, Matured, Closed]
- reason: string
- bcode: string
- adviserid: string
- old: boolean
- special: boolean
- nominee: string
- relation: string
- naddress: string
- ocode: string

**Response:** JSON array  
**Errors:** 400 / 401 / 500  

---

### POST /account/searchCount
**Purpose:** Count accounts  
**Request:** Same fields as /account/search  
**Response:** number  
**Errors:** Same as /account/search  

---

## 6️⃣ Transaction APIs

### POST /transaction/search
**Purpose:** Search transactions  
**Request Body Fields:**
- transactionno: string
- tdate: date
- particulars: string
- ttype: string [
    Deposit, Withdraw, Yearly Interest, Maturity Interest,
    Matrity Transfer, Loan Payment,
    Reverse Entry(Dr), Reverse Entry(Cr),
    Transfer In, Transfer Out, SMS Charge,
    Annual Maintenance Charge
  ]
- bcode: string
- memberno: string
- accountno: string
- adviserid: string
- amount: float
- cbalance: float
- fyear: string
- period: string
- transactionby: string
- frombranch: boolean
- bankaccountno: string
- newaccount: boolean
- note: string
- transactionid: string
- ocode: string

**Response:** JSON array  

---

### POST /transaction/searchCount
**Purpose:** Count transactions  
**Response:** number  
**Errors:** Same as /transaction/search  

---

### GET /transaction/availableBalance/{ocode}/{accountno}
**Purpose:** Get account available balance  
Path Parameters:
- ocode: string
- accountno: string  
**Response:** number  
**Errors:** 400 / 401 / 404 / 500  

---

### ✅ Notes
- All filters are optional  
- Dates use format: `YYYY-MM-DD`
- Exact match filters unless backend supports LIKE

