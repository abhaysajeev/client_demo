# ERPNext Mobile App API Documentation

**Version:** 1.0  
**Base URL:** `http://192.168.0.66:8001/api/method/client_demo.services`  
**Last Updated:** January 27, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Response Formats](#common-response-formats)
4. [Error Handling](#error-handling)
5. [API Endpoints](#api-endpoints)
   - [Helper Functions](#helper-functions)
   - [Attendance & Check-in](#attendance--check-in)
   - [Leave Management](#leave-management)
6. [Data Models](#data-models)
7. [Usage Examples](#usage-examples)

---

## Overview

This API provides endpoints for an Android mobile application to interact with ERPNext for:
- Employee attendance tracking (check-in/check-out)
- Employee dashboard with work hours calculation
- Leave application management
- Manager approval workflows

All endpoints accept JSON payloads and return JSON responses.

---

## Authentication

### Current Implementation
All endpoints are currently marked with `allow_guest=True` for testing purposes.

### Production Requirements

> [!WARNING]
> **For production deployment**, you must implement proper authentication:

**Option 1: API Key Authentication**
```http
GET /api/method/... HTTP/1.1
Authorization: token <api_key>:<api_secret>
```

**Option 2: Session-based Authentication**
```http
POST /api/method/frappe.auth.get_logged_user
Content-Type: application/json

{
  "usr": "user@example.com",
  "pwd": "password"
}
```

Then include the session cookie in subsequent requests.

---

## Common Response Formats

### Success Response
```json
{
  "message": {
    "success": true,
    "data": { ... }
  }
}
```

### Error Response
```json
{
  "message": {
    "success": false,
    "message": "Error description"
  }
}
```

### ERPNext System Errors
```json
{
  "exception": "Error type",
  "exc_type": "ExceptionType",
  "_server_messages": "...",
  "exc": "Full traceback"
}
```

---

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response normally |
| 403 | Forbidden | Check authentication/permissions |
| 404 | Not Found | Verify endpoint URL |
| 417 | Validation Error | Check request parameters |
| 500 | Server Error | Retry or contact support |

### Application-Level Errors

Check the `success` field in the response:
```kotlin
if (response.message.success == false) {
    // Handle error
    val errorMessage = response.message.message
}
```

---

## API Endpoints

### Helper Functions

#### Validate Employee ID

**Endpoint:** `helper_functions.get_employee_docname`  
**Method:** POST  
**Description:** Validates if an Employee ID exists in the system

**Request:**
```json
{
  "employee_input": "AMAL R"
}
```

**Response (Success):**
```json
{
  "message": "AMAL R"
}
```

**Response (Not Found):**
```json
{
  "message": null
}
```

**Android Example:**
```kotlin
data class ValidateEmployeeRequest(
    val employee_input: String
)

suspend fun validateEmployee(employeeId: String): String? {
    val response = apiService.post(
        "helper_functions.get_employee_docname",
        ValidateEmployeeRequest(employeeId)
    )
    return response.message
}
```

---

### Attendance & Check-in

#### 1. Mark Attendance (Check-in/Check-out)

**Endpoint:** `checkin_dummy.mark_attendance`  
**Method:** POST  
**Description:** Records employee check-in or check-out. Automatically determines IN/OUT based on last record.

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| employee | String | ✅ Yes | Employee ID (e.g., "AMAL R") |
| log_type | String | ❌ No | "IN" or "OUT" (auto-detected if omitted) |
| device_id | String | ❌ No | Device identifier (defaults to "Remote") |
| shift | String | ❌ No | Shift name (auto-fetched if omitted) |

**Request:**
```json
{
  "employee": "AMAL R"
}
```

**Response (Success):**
```json
{
  "message": {
    "success": true,
    "message": "Attendance recorded successfully as IN",
    "log_type": "IN",
    "time": "2026-01-27 11:42:11.962345"
  }
}
```

**Response (Employee Not Found):**
```json
{
  "message": {
    "success": false,
    "message": "Employee AMAL R not found"
  }
}
```

**Android Example:**
```kotlin
data class MarkAttendanceRequest(
    val employee: String,
    val log_type: String? = null,
    val device_id: String? = null,
    val shift: String? = null
)

data class MarkAttendanceResponse(
    val success: Boolean,
    val message: String,
    val log_type: String?,
    val time: String?
)

suspend fun markAttendance(employeeId: String): MarkAttendanceResponse {
    val response = apiService.post(
        "checkin_dummy.mark_attendance",
        MarkAttendanceRequest(employee = employeeId)
    )
    return response.message
}
```

**Important Notes:**
- If last log was "IN", next will be "OUT" (and vice versa)
- Time is automatically set to current timestamp
- Device ID defaults to "Remote" for mobile app

---

#### 2. Get Employee Dashboard Data

**Endpoint:** `checkin_dummy.get_employee_details`  
**Method:** POST  
**Description:** Fetches comprehensive dashboard data including today's attendance, weekly/monthly summaries

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | String | ✅ Yes | Employee's email/user ID |
| select_date | String | ❌ No | Date in YYYY-MM-DD format (defaults to today) |

**Request:**
```json
{
  "user_id": "amal.r@softlandindia.co.in",
  "select_date": "2026-01-27"
}
```

**Response (Success):**
```json
{
  "message": {
    "success": true,
    "employee_details": {
      "name": "AMAL R",
      "department": "Web Applications Department - SIL",
      "designation": "Junior Software Programmer"
    },
    "selected_date_data": {
      "date": "2026-01-27",
      "daily_working_hours": 0.0,
      "entry_time": "11:42",
      "exit_time": null,
      "checkin_pairs": [
        {
          "in_time": "11:42",
          "out_time": null,
          "duration": null
        }
      ],
      "status": "Present"
    },
    "weekly_summary": {
      "total_hours_worked": 0.0,
      "average_work_hours": 0.0,
      "days_worked": 0,
      "total_working_days_in_period": 1
    },
    "monthly_summary": {
      "total_hours_worked": 0.0,
      "average_work_hours": 0.0,
      "days_worked": 0,
      "total_working_days_in_period": 18
    }
  }
}
```

**Response (User Not Found):**
```json
{
  "message": {
    "success": false,
    "message": "User user@example.com not found"
  }
}
```

**Status Values:**
- `"Present"` - Employee checked in
- `"Absent"` - No check-in record
- `"Holiday"` - Official holiday
- `"On Leave"` - Approved leave

**Android Example:**
```kotlin
data class DashboardRequest(
    val user_id: String,
    val select_date: String? = null
)

data class DashboardResponse(
    val success: Boolean,
    val employee_details: EmployeeDetails?,
    val selected_date_data: DailyData?,
    val weekly_summary: Summary?,
    val monthly_summary: Summary?
)

data class EmployeeDetails(
    val name: String,
    val department: String,
    val designation: String
)

data class DailyData(
    val date: String,
    val daily_working_hours: Double,
    val entry_time: String?,
    val exit_time: String?,
    val checkin_pairs: List<CheckinPair>,
    val status: String
)

data class CheckinPair(
    val in_time: String?,
    val out_time: String?,
    val duration: Double?
)

data class Summary(
    val total_hours_worked: Double,
    val average_work_hours: Double,
    val days_worked: Int,
    val total_working_days_in_period: Int
)
```

---

#### 3. Get Employee Check-ins

**Endpoint:** `checkin_dummy.get_employee_checkins`  
**Method:** POST  
**Description:** Fetches all check-in records for an employee within a date range

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| employee | String | ✅ Yes | Employee ID |
| from_date | String | ✅ Yes | Start date (YYYY-MM-DD) |
| to_date | String | ✅ Yes | End date (YYYY-MM-DD) |

**Request:**
```json
{
  "employee": "AMAL R",
  "from_date": "2026-01-01",
  "to_date": "2026-01-31"
}
```

**Response (Success):**
```json
{
  "message": {
    "success": true,
    "count": 2,
    "data": [
      {
        "name": "CHKIN-00001",
        "time": "2026-01-27 11:42:11",
        "log_type": "IN"
      },
      {
        "name": "CHKIN-00002",
        "time": "2026-01-27 18:30:00",
        "log_type": "OUT"
      }
    ]
  }
}
```

---

### Leave Management

#### 1. Apply for Leave

**Endpoint:** `leave_application.apply_leave`  
**Method:** POST  
**Description:** Submit a new leave application

> [!IMPORTANT]
> **This endpoint requires authentication.** Guest users will receive a permission error.

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| employee | String | ✅ Yes | Employee ID |
| leave_type | String | ✅ Yes | Leave type name (e.g., "Casual Leave") |
| from_date | String | ✅ Yes | Start date (YYYY-MM-DD) |
| to_date | String | ✅ Yes | End date (YYYY-MM-DD) |
| reason | String | ✅ Yes | Reason for leave |
| half_day | Integer | ❌ No | 1 for half day, 0 for full day |

**Request:**
```json
{
  "employee": "AMAL R",
  "leave_type": "Casual Leave",
  "from_date": "2026-02-01",
  "to_date": "2026-02-02",
  "reason": "Personal work",
  "half_day": 0
}
```

**Response (Success):**
```json
{
  "message": {
    "status": "success",
    "message": "Leave Application HR-LAP-00001 created. Pending approval from VINOD K",
    "leave_name": "HR-LAP-00001"
  }
}
```

**Response (Employee Not Found):**
```json
{
  "message": {
    "status": "error",
    "message": "Employee not found: INVALID ID"
  }
}
```

**Response (Invalid Leave Type):**
```json
{
  "message": {
    "status": "error",
    "message": "Leave Type not found: Invalid Leave"
  }
}
```

---

#### 2. Get Available Leave Types

**Endpoint:** `leave_application.get_leave_types`  
**Method:** POST  
**Description:** Fetches all available leave types in the system

**Request:**
```json
{}
```

**Response (Success):**
```json
{
  "message": [
    "Casual Leave",
    "Sick Leave",
    "Privilege Leave",
    "Compensatory Off",
    "Leave Without Pay"
  ]
}
```

---

#### 3. Get Leave Approver

**Endpoint:** `leave_application.get_leave_approver`  
**Method:** POST  
**Description:** Gets the approver (reporting manager) for an employee

**Request:**
```json
{
  "employee": "AMAL R"
}
```

**Response (Success):**
```json
{
  "message": "VINOD K"
}
```

**Response (No Approver):**
```json
{
  "message": null
}
```

---

#### 4. Get Unapproved Leaves (Manager View)

**Endpoint:** `leave_application.get_unapproved_leaves`  
**Method:** POST  
**Description:** Fetches all pending leave applications for a manager's reportees

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | String | ✅ Yes | Manager's email/user ID |

**Request:**
```json
{
  "user_id": "vinod@softlandindia.co.in"
}
```

**Response (Success):**
```json
{
  "message": {
    "status": "success",
    "manager": "VINOD K",
    "reportees_count": 1,
    "leave_count": 0,
    "leaves": []
  }
}
```

**Response (With Pending Leaves):**
```json
{
  "message": {
    "status": "success",
    "manager": "VINOD K",
    "reportees_count": 3,
    "leave_count": 2,
    "leaves": [
      {
        "name": "HR-LAP-00001",
        "employee": "AMAL R",
        "employee_name": "Amal R",
        "leave_type": "Casual Leave",
        "from_date": "2026-02-01",
        "to_date": "2026-02-02",
        "description": "Personal work",
        "status": "Open",
        "docstatus": 0
      }
    ]
  }
}
```

---

#### 5. Approve Leave

**Endpoint:** `leave_application.approve_leave`  
**Method:** POST  
**Description:** Approve a pending leave application (for managers)

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| leave_name | String | ✅ Yes | Leave Application ID |
| employee | String | ✅ Yes | Manager's Employee ID |

**Request:**
```json
{
  "leave_name": "HR-LAP-00001",
  "employee": "VINOD K"
}
```

**Response (Success):**
```json
{
  "message": {
    "status": "success",
    "message": "Leave approved: Approved by VINOD K"
  }
}
```

**Response (Already Approved):**
```json
{
  "message": {
    "status": "error",
    "message": "Leave already approved by VINOD K"
  }
}
```

**Response (Already Submitted):**
```json
{
  "message": {
    "status": "error",
    "message": "Leave Application already submitted"
  }
}
```

---

#### 6. Get Leave Application Status

**Endpoint:** `leave_application.get_pending_leave_application_status`  
**Method:** POST  
**Description:** Gets leave application history for an employee (approved and pending)

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| employee | String | ✅ Yes | Employee ID |
| month | String | ❌ No | Month number (1-12) or name |
| year | Integer | ❌ No | Year (defaults to current year) |

**Request:**
```json
{
  "employee": "AMAL R",
  "month": "2",
  "year": 2026
}
```

**Response (Success):**
```json
{
  "message": {
    "success": true,
    "message": "Leave applications for AMAL R in February 2026",
    "approved": [
      {
        "name": "HR-LAP-00001",
        "employee": "AMAL R",
        "leave_type": "Casual Leave",
        "from_date": "2026-02-01",
        "to_date": "2026-02-02",
        "custom_approved_by": "Approved by VINOD K",
        "status": "Open"
      }
    ],
    "not_approved": [],
    "total": 1
  }
}
```

**Response (No Leaves):**
```json
{
  "message": {
    "success": true,
    "message": "No leave applications found for AMAL R in February 2026",
    "approved": [],
    "not_approved": []
  }
}
```

---

## Data Models

### Employee
```kotlin
data class Employee(
    val name: String,          // Unique ID (e.g., "AMAL R")
    val employee_name: String, // Full name
    val department: String,
    val designation: String,
    val user_id: String,       // Email
    val reports_to: String?,   // Manager's Employee ID
    val default_shift: String?
)
```

### Employee Checkin
```kotlin
data class EmployeeCheckin(
    val name: String,          // Checkin ID
    val employee: String,      // Employee ID
    val time: String,          // ISO timestamp
    val log_type: String,      // "IN" or "OUT"
    val device_id: String?,
    val shift: String?
)
```

### Leave Application
```kotlin
data class LeaveApplication(
    val name: String,              // Leave Application ID
    val employee: String,          // Employee ID
    val employee_name: String,
    val leave_type: String,
    val from_date: String,         // YYYY-MM-DD
    val to_date: String,
    val description: String,
    val status: String,            // "Open", "Approved", "Rejected"
    val docstatus: Int,            // 0=Draft, 1=Submitted, 2=Cancelled
    val custom_approved_by: String? // Approval message
)
```

---

## Usage Examples

### Complete Android Integration Example

```kotlin
// API Service Interface
interface ERPNextApiService {
    @POST("api/method/client_demo.services.{endpoint}")
    suspend fun post(
        @Path("endpoint") endpoint: String,
        @Body request: Any
    ): Response<ApiResponse>
}

// Repository Layer
class AttendanceRepository(private val apiService: ERPNextApiService) {
    
    suspend fun markAttendance(employeeId: String): Result<MarkAttendanceResponse> {
        return try {
            val response = apiService.post(
                "checkin_dummy.mark_attendance",
                mapOf("employee" to employeeId)
            )
            if (response.isSuccessful) {
                Result.success(response.body()!!.message)
            } else {
                Result.failure(Exception("Failed to mark attendance"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getDashboardData(userId: String): Result<DashboardResponse> {
        return try {
            val response = apiService.post(
                "checkin_dummy.get_employee_details",
                mapOf("user_id" to userId)
            )
            if (response.isSuccessful) {
                Result.success(response.body()!!.message)
            } else {
                Result.failure(Exception("Failed to fetch dashboard"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// ViewModel
class DashboardViewModel(private val repository: AttendanceRepository) : ViewModel() {
    
    private val _dashboardData = MutableLiveData<DashboardResponse>()
    val dashboardData: LiveData<DashboardResponse> = _dashboardData
    
    fun loadDashboard(userId: String) {
        viewModelScope.launch {
            repository.getDashboardData(userId).onSuccess { data ->
                _dashboardData.value = data
            }.onFailure { error ->
                // Handle error
            }
        }
    }
    
    fun markAttendance(employeeId: String) {
        viewModelScope.launch {
            repository.markAttendance(employeeId).onSuccess { response ->
                // Refresh dashboard
                loadDashboard(userId)
            }
        }
    }
}
```

### Retrofit Configuration

```kotlin
object ApiClient {
    private const val BASE_URL = "http://192.168.0.66:8001/"
    
    val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .client(
                OkHttpClient.Builder()
                    .connectTimeout(30, TimeUnit.SECONDS)
                    .readTimeout(30, TimeUnit.SECONDS)
                    .addInterceptor { chain ->
                        val request = chain.request().newBuilder()
                            .addHeader("Content-Type", "application/json")
                            .build()
                        chain.proceed(request)
                    }
                    .build()
            )
            .build()
    }
    
    val apiService: ERPNextApiService by lazy {
        retrofit.create(ERPNextApiService::class.java)
    }
}
```

---

## Important Notes

1. **Employee IDs**: Always use the unique Employee `name` field (e.g., "AMAL R"), not the full name
2. **Date Format**: All dates must be in `YYYY-MM-DD` format
3. **Time Format**: Timestamps are in ISO format: `YYYY-MM-DD HH:MM:SS.microseconds`
4. **Authentication**: Implement proper authentication before production deployment
5. **Error Handling**: Always check the `success` field in responses
6. **Network Timeout**: Set appropriate timeouts (30+ seconds recommended)
7. **Permission Errors**: Leave application endpoints require authenticated users with proper roles

---

## Testing Checklist

- [ ] Mark attendance (check-in)
- [ ] Mark attendance (check-out)
- [ ] Get dashboard data
- [ ] Get employee check-ins history
- [ ] Get available leave types
- [ ] Apply for leave (with authentication)
- [ ] Get manager's pending leaves
- [ ] Approve leave (as manager)
- [ ] Get leave status history
- [ ] Handle network errors gracefully
- [ ] Handle permission errors
- [ ] Test with invalid employee IDs
- [ ] Test with invalid date formats

---

## Support

For API issues or questions, contact:
- **Email**: sil@gmail.com
- **API Version**: 1.0
- **ERPNext Version**: v15

---

**Document Version:** 1.0  
**Last Updated:** January 27, 2026
