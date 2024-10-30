from locust import TaskSet, HttpUser, between, task
import json


class MyAPITasks(TaskSet):

    def on_start(self):
        self.create_seller_user(
            {
                "username": f"{self.user.username}",
                "password": "ABC==testpassword1",
            }
        )
        self.login(
            {
                "username": f"{self.user.username}",
                "password": "ABC==testpassword1",
            }
        )

    def create_seller_user(self, seller_data):
        with self.client.post(
            "/seller/create-seller/",
            data=json.dumps(seller_data),
            headers={"Content-Type": "application/json"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                return
            else:
                response.failure("Create seller failed")

    def login(self, login_data):
        with self.client.post(
            "/auth/token/",
            data=json.dumps(login_data),
            headers={"Content-Type": "application/json"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.token = response.json().get("access")
                if self.token:
                    self.headers = {
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json",
                    }
            else:
                response.failure("Login failed")

    @task
    def test_balance_request_and_approve_it(self):
        # Step 1: Create a balance request
        with self.client.post(
            "/billing/balance-request/",
            data=json.dumps({"amount": 1000}),
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code == 201:
                response_data = response.json()
                balance_request_id = response_data.get("id")

                # Step 2: Approve the balance request if creation was successful
                if balance_request_id:
                    approve_url = (
                        f"/billing/balance-request/{balance_request_id}/approve/"
                    )
                    self.client.patch(
                        approve_url,
                        headers=self.headers,
                    )
            else:
                response.failure("Balance request creation failed")

    @task(5)
    def test_recharge_mobiles(self):
        self.client.post(
            "/billing/recharge-mobile/",
            data=json.dumps({"amount": 10, "phone_number": "09183332211"}),
            headers=self.headers,
        )


class MyAPIUser(HttpUser):
    wait_time = between(0.1, 0.5)
    tasks = [MyAPITasks]

    # This will keep track of the number of user instances
    user_counter = 0

    def on_start(self):
        # Use the class variable to create a unique username
        MyAPIUser.user_counter += 1
        self.username = f"user{MyAPIUser.user_counter}"
