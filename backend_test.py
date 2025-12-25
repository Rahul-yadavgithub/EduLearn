import requests
import sys
import json
from datetime import datetime
import uuid

class EducationPlatformTester:
    def __init__(self, base_url="https://learnhub-671.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.student_token = None
        self.teacher_token = None
        self.student_user = None
        self.teacher_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.paper_id = None
        self.doubt_id = None
        self.result_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, auth_type=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        # Add authentication
        if auth_type == 'student' and self.student_token:
            test_headers['Authorization'] = f'Bearer {self.student_token}'
        elif auth_type == 'teacher' and self.teacher_token:
            test_headers['Authorization'] = f'Bearer {self.teacher_token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "endpoint": endpoint
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "error": str(e),
                "endpoint": endpoint
            })
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_seed_data(self):
        """Test seeding sample data"""
        return self.run_test("Seed Data", "POST", "seed", 200)

    def test_student_registration(self):
        """Test student registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        student_data = {
            "name": f"Test Student {timestamp}",
            "email": f"student{timestamp}@test.com",
            "password": "TestPass123!",
            "role": "student"
        }
        
        success, response = self.run_test("Student Registration", "POST", "auth/register", 200, student_data)
        if success and 'token' in response:
            self.student_token = response['token']
            self.student_user = response['user']
            print(f"   Student registered: {self.student_user['email']}")
        return success

    def test_teacher_registration(self):
        """Test teacher registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        teacher_data = {
            "name": f"Test Teacher {timestamp}",
            "email": f"teacher{timestamp}@test.com",
            "password": "TestPass123!",
            "role": "teacher"
        }
        
        success, response = self.run_test("Teacher Registration", "POST", "auth/register", 200, teacher_data)
        if success and 'token' in response:
            self.teacher_token = response['token']
            self.teacher_user = response['user']
            print(f"   Teacher registered: {self.teacher_user['email']}")
        return success

    def test_student_login(self):
        """Test student login"""
        if not self.student_user:
            return False
            
        login_data = {
            "email": self.student_user['email'],
            "password": "TestPass123!"
        }
        
        success, response = self.run_test("Student Login", "POST", "auth/login", 200, login_data)
        if success and 'token' in response:
            self.student_token = response['token']
        return success

    def test_teacher_login(self):
        """Test teacher login"""
        if not self.teacher_user:
            return False
            
        login_data = {
            "email": self.teacher_user['email'],
            "password": "TestPass123!"
        }
        
        success, response = self.run_test("Teacher Login", "POST", "auth/login", 200, login_data)
        if success and 'token' in response:
            self.teacher_token = response['token']
        return success

    def test_get_current_user(self):
        """Test getting current user info"""
        success, _ = self.run_test("Get Current User (Student)", "GET", "auth/me", 200, auth_type='student')
        return success

    def test_get_papers(self):
        """Test getting papers list"""
        success, response = self.run_test("Get Papers", "GET", "papers", 200)
        if success and response:
            papers = response if isinstance(response, list) else []
            print(f"   Found {len(papers)} papers")
            if papers:
                self.paper_id = papers[0].get('paper_id')
                print(f"   Using paper: {self.paper_id}")
        return success

    def test_get_single_paper(self):
        """Test getting a single paper"""
        if not self.paper_id:
            print("   Skipping - No paper ID available")
            return True
            
        success, _ = self.run_test("Get Single Paper", "GET", f"papers/{self.paper_id}", 200)
        return success

    def test_create_paper(self):
        """Test creating a paper (teacher only)"""
        paper_data = {
            "title": "Test Paper - Physics",
            "subject": "Physics",
            "exam_type": "JEE",
            "sub_type": "JEE Mains",
            "questions": [
                {
                    "question_id": "test_q1",
                    "question_text": "What is the SI unit of force?",
                    "subject": "Physics",
                    "options": {"A": "Newton", "B": "Joule", "C": "Watt", "D": "Pascal"},
                    "correct_answer": "A",
                    "explanation": "Newton is the SI unit of force",
                    "difficulty": "Easy"
                }
            ]
        }
        
        success, response = self.run_test("Create Paper", "POST", "papers", 200, paper_data, auth_type='teacher')
        if success and response:
            created_paper_id = response.get('paper_id')
            if created_paper_id:
                print(f"   Created paper: {created_paper_id}")
        return success

    def test_create_doubt(self):
        """Test creating a doubt (student only)"""
        doubt_data = {
            "subject": "Physics",
            "question_text": "Can you explain Newton's first law of motion?"
        }
        
        success, response = self.run_test("Create Doubt", "POST", "doubts", 200, doubt_data, auth_type='student')
        if success and response:
            self.doubt_id = response.get('doubt_id')
            print(f"   Created doubt: {self.doubt_id}")
        return success

    def test_get_doubts(self):
        """Test getting doubts list"""
        success, response = self.run_test("Get Doubts (Student)", "GET", "doubts", 200, auth_type='student')
        if success and response:
            doubts = response if isinstance(response, list) else []
            print(f"   Found {len(doubts)} doubts")
        return success

    def test_answer_doubt(self):
        """Test answering a doubt (teacher only)"""
        if not self.doubt_id:
            print("   Skipping - No doubt ID available")
            return True
            
        answer_data = {
            "answer_text": "Newton's first law states that an object at rest stays at rest and an object in motion stays in motion unless acted upon by an external force."
        }
        
        success, _ = self.run_test("Answer Doubt", "PUT", f"doubts/{self.doubt_id}/answer", 200, answer_data, auth_type='teacher')
        return success

    def test_submit_test(self):
        """Test submitting a test (student only)"""
        if not self.paper_id:
            print("   Skipping - No paper ID available")
            return True
            
        submission_data = {
            "paper_id": self.paper_id,
            "answers": {"q1": "B", "q2": "C"},  # Sample answers
            "time_taken": 1800  # 30 minutes
        }
        
        success, response = self.run_test("Submit Test", "POST", "tests/submit", 200, submission_data, auth_type='student')
        if success and response:
            self.result_id = response.get('result_id')
            print(f"   Test submitted, result: {self.result_id}")
        return success

    def test_get_test_results(self):
        """Test getting test results"""
        success, response = self.run_test("Get Test Results", "GET", "tests/results", 200, auth_type='student')
        if success and response:
            results = response if isinstance(response, list) else []
            print(f"   Found {len(results)} test results")
        return success

    def test_get_single_result(self):
        """Test getting a single test result"""
        if not self.result_id:
            print("   Skipping - No result ID available")
            return True
            
        success, _ = self.run_test("Get Single Result", "GET", f"tests/results/{self.result_id}", 200, auth_type='student')
        return success

    def test_get_progress(self):
        """Test getting student progress"""
        success, response = self.run_test("Get Progress", "GET", "progress", 200, auth_type='student')
        if success and response:
            print(f"   Progress data: {response.get('total_tests', 0)} tests taken")
        return success

    def test_generate_paper(self):
        """Test AI paper generation (teacher only)"""
        generation_data = {
            "num_questions": 2,
            "subject": "Physics",
            "difficulty": "Medium",
            "purpose": "JEE",
            "sub_type": "JEE Mains",
            "language": "English"
        }
        
        success, response = self.run_test("Generate Paper", "POST", "generate-paper", 200, generation_data, auth_type='teacher')
        if success and response:
            questions = response.get('questions', [])
            print(f"   Generated {len(questions)} questions")
        return success

    def test_logout(self):
        """Test logout"""
        success, _ = self.run_test("Logout", "POST", "auth/logout", 200, auth_type='student')
        return success

def main():
    print("🚀 Starting Education Platform API Tests")
    print("=" * 50)
    
    tester = EducationPlatformTester()
    
    # Test sequence
    tests = [
        ("Root API", tester.test_root_endpoint),
        ("Seed Data", tester.test_seed_data),
        ("Student Registration", tester.test_student_registration),
        ("Teacher Registration", tester.test_teacher_registration),
        ("Student Login", tester.test_student_login),
        ("Teacher Login", tester.test_teacher_login),
        ("Get Current User", tester.test_get_current_user),
        ("Get Papers", tester.test_get_papers),
        ("Get Single Paper", tester.test_get_single_paper),
        ("Create Paper", tester.test_create_paper),
        ("Create Doubt", tester.test_create_doubt),
        ("Get Doubts", tester.test_get_doubts),
        ("Answer Doubt", tester.test_answer_doubt),
        ("Submit Test", tester.test_submit_test),
        ("Get Test Results", tester.test_get_test_results),
        ("Get Single Result", tester.test_get_single_result),
        ("Get Progress", tester.test_get_progress),
        ("Generate Paper", tester.test_generate_paper),
        ("Logout", tester.test_logout),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            tester.failed_tests.append({
                "test": test_name,
                "error": str(e)
            })
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.failed_tests:
        print(f"\n❌ Failed Tests ({len(tester.failed_tests)}):")
        for failure in tester.failed_tests:
            print(f"   • {failure['test']}: {failure.get('error', f\"Expected {failure.get('expected')}, got {failure.get('actual')}\")}")
    
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())