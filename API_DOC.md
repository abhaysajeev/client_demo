# ERPNext Mobile App API Documentation

**Version:** 2.0  
**Base URL Format:** `<base_url>/api/method/client_demo.services`  
**Last Updated:** January 27, 2026

---

# PART 1: ATTENDANCE & LEAVE APIs

---

## 1. Mark Attendance (Biometric/Direct)

**Endpoint:** `<base_url>/api/method/client_demo.services.checkin_dummy.mark_attendance`  
**Method:** POST

### Input Parameters
```json
{
  "employee": "AMAL R"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| employee | String | ✅ Yes | Employee unique ID |
| log_type | String | ❌ No | "IN" or "OUT" (auto-detected) |

### Output Format
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

---

## 2. Get Employee Dashboard

**Endpoint:** `<base_url>/api/method/client_demo.services.checkin_dummy.get_employee_details`  
**Method:** POST

### Input Parameters
```json
{
  "user_id": "amal.r@softlandindia.co.in",
  "select_date": "2026-01-27"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | String | ✅ Yes | Employee's email address |
| select_date | String | ❌ No | Date in YYYY-MM-DD format |

### Output Format
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
      "daily_working_hours": 8.5,
      "entry_time": "09:00",
      "exit_time": "17:30",
      "status": "Present"
    },
    "weekly_summary": {
      "total_hours_worked": 42.5,
      "average_work_hours": 8.5,
      "days_worked": 5
    },
    "monthly_summary": {
      "total_hours_worked": 170.0,
      "average_work_hours": 8.5,
      "days_worked": 20
    }
  }
}
```

---

## 3. Apply for Leave

**Endpoint:** `<base_url>/api/method/client_demo.services.leave_application.apply_leave`  
**Method:** POST

### Input Parameters
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

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| employee | String | ✅ Yes | Employee unique ID |
| leave_type | String | ✅ Yes | Leave type name |
| from_date | String | ✅ Yes | Start date (YYYY-MM-DD) |
| to_date | String | ✅ Yes | End date (YYYY-MM-DD) |
| reason | String | ✅ Yes | Reason for leave |
| half_day | Integer | ❌ No | 1 for half day, 0 for full day |

### Output Format
```json
{
  "message": {
    "status": "success",
    "message": "Leave Application HR-LAP-00001 created. Pending approval from VINOD K",
    "leave_name": "HR-LAP-00001"
  }
}
```

---

## 4. Get Available Leave Types

**Endpoint:** `<base_url>/api/method/client_demo.services.leave_application.get_leave_types`  
**Method:** POST

### Output Format
```json
{
  "message": [
    "Casual Leave",
    "Sick Leave",
    "Privilege Leave"
  ]
}
```

---

## 5. Get Unapproved Leaves (Manager)

**Endpoint:** `<base_url>/api/method/client_demo.services.leave_application.get_unapproved_leaves`  
**Method:** POST

### Input Parameters
```json
{
  "user_id": "vinod@softlandindia.co.in"
}
```

### Output Format
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
        "leave_type": "Casual Leave",
        "from_date": "2026-02-01",
        "to_date": "2026-02-02",
        "status": "Open"
      }
    ]
  }
}
```

---

## 6. Approve Leave (Manager)

**Endpoint:** `<base_url>/api/method/client_demo.services.leave_application.approve_leave`  
**Method:** POST

### Input Parameters
```json
{
  "leave_name": "HR-LAP-00001",
  "employee": "VINOD K"
}
```

### Output Format
```json
{
  "message": {
    "status": "success",
    "message": "Leave approved: Approved by VINOD K"
  }
}
```

---

# PART 2: REMOTE ATTENDANCE APIs

---

## 7. Mark Remote Attendance

**Endpoint:** `<base_url>/api/method/client_demo.services.remote_attendance.mark_remote_attendance`  
**Method:** POST

### Input Parameters
```json
{
  "employee": "AMAL R",
  "latitude": 10.8505159,
  "longitude": 76.2710833,
  "location_type": "Work From Home",
  "device_info": "Samsung Galaxy S21",
  "remarks": "Working from home"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| employee | String | ✅ Yes | Employee unique ID |
| latitude | Float | ✅ Yes | GPS latitude |
| longitude | Float | ✅ Yes | GPS longitude |
| location_type | String | ✅ For IN | "Work From Home" / "Field" / "Service Center" |
| device_info | String | ❌ No | Device identifier |
| remarks | String | ❌ No | Optional notes |

### Output Format
```json
{
  "message": {
    "success": true,
    "name": "RA-2026-00001",
    "log_type": "IN",
    "time": "2026-01-27 09:00:00",
    "location_type": "Work From Home",
    "workflow_state": "Pending",
    "message": "Attendance marked as IN. Pending approval from VINOD K"
  }
}
```

---

## 8. Get Today Attendance Status

**Endpoint:** `<base_url>/api/method/client_demo.services.remote_attendance.get_today_attendance_status`  
**Method:** POST

### Input Parameters
```json
{
  "employee": "AMAL R"
}
```

### Output Format
```json
{
  "message": {
    "success": true,
    "date": "2026-01-27",
    "next_log_type": "OUT",
    "total_checkins_today": 1,
    "pending_approvals": 0,
    "last_checkin": {
      "name": "RA-2026-00001",
      "log_type": "IN",
      "time": "2026-01-27 09:00:00",
      "status": "Approved",
      "source": "remote"
    },
    "is_first_of_day": false
  }
}
```

---

## 9. Get Location Type Options

**Endpoint:** `<base_url>/api/method/client_demo.services.remote_attendance.get_location_type_options`  
**Method:** POST

### Output Format
```json
{
  "message": [
    "Work From Home",
    "Field",
    "Service Center"
  ]
}
```

---

## 10. Get Pending Remote Attendance

**Endpoint:** `<base_url>/api/method/client_demo.services.remote_attendance.get_pending_remote_attendance`  
**Method:** POST

### Input Parameters
```json
{
  "employee": "AMAL R"
}
```

### Output Format
```json
{
  "message": {
    "success": true,
    "count": 1,
    "data": [
      {
        "name": "RA-2026-00001",
        "log_type": "IN",
        "time": "2026-01-27 09:00:00",
        "location_type": "Work From Home",
        "workflow_state": "Pending",
        "latitude": 10.8505159,
        "longitude": 76.2710833
      }
    ]
  }
}
```

---

## 11. Get Remote Attendance History

**Endpoint:** `<base_url>/api/method/client_demo.services.remote_attendance.get_remote_attendance_history`  
**Method:** POST

### Input Parameters
```json
{
  "employee": "AMAL R",
  "from_date": "2026-01-01",
  "to_date": "2026-01-31"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| employee | String | ✅ Yes | Employee unique ID |
| from_date | String | ❌ No | Start date filter |
| to_date | String | ❌ No | End date filter |

### Output Format
```json
{
  "message": {
    "success": true,
    "count": 5,
    "data": [
      {
        "name": "RA-2026-00001",
        "log_type": "IN",
        "time": "2026-01-27 09:00:00",
        "location_type": "Work From Home",
        "workflow_state": "Approved",
        "approved_by": "VINOD K",
        "linked_checkin": "EMP-CKIN-00123"
      }
    ]
  }
}
```

---

## 12. Cancel Remote Attendance

**Endpoint:** `<base_url>/api/method/client_demo.services.remote_attendance.cancel_remote_attendance`  
**Method:** POST

### Input Parameters
```json
{
  "name": "RA-2026-00001",
  "employee": "AMAL R"
}
```

### Output Format
```json
{
  "message": {
    "success": true,
    "message": "Remote Attendance RA-2026-00001 cancelled successfully"
  }
}
```

---

## 13. Get Today Checkin Pairs

**Endpoint:** `<base_url>/api/method/client_demo.services.remote_attendance.get_today_checkin_pairs`  
**Method:** POST

### Input Parameters
```json
{
  "employee": "AMAL R"
}
```

### Output Format
```json
{
  "message": {
    "success": true,
    "date": "2026-01-27",
    "pairs": [
      {
        "in_time": "09:00",
        "out_time": "13:00",
        "location_type": "Work From Home",
        "duration_hours": 4.0,
        "source": "remote"
      }
    ],
    "total_hours": 4.0
  }
}
```

---

## 14. Get Pending Approvals (Manager)

**Endpoint:** `<base_url>/api/method/client_demo.services.remote_attendance.get_pending_approvals`  
**Method:** POST

### Input Parameters
```json
{
  "user_id": "vinod@softlandindia.co.in"
}
```

### Output Format
```json
{
  "message": {
    "success": true,
    "manager": "VINOD K",
    "reportees_count": 3,
    "pending_count": 2,
    "data": [
      {
        "name": "RA-2026-00001",
        "employee": "AMAL R",
        "employee_name": "AMAL R",
        "log_type": "IN",
        "time": "2026-01-27 09:00:00",
        "location_type": "Work From Home",
        "latitude": 10.8505159,
        "longitude": 76.2710833
      }
    ]
  }
}
```

---

## 15. Approve Remote Attendance (Manager)

**Endpoint:** `<base_url>/api/method/client_demo.services.remote_attendance.approve_remote_attendance`  
**Method:** POST

### Input Parameters
```json
{
  "name": "RA-2026-00001",
  "manager": "VINOD K"
}
```

### Output Format
```json
{
  "message": {
    "success": true,
    "message": "Approved and checkin created",
    "remote_attendance": "RA-2026-00001",
    "employee_checkin": "EMP-CKIN-00123"
  }
}
```

---

## 16. Reject Remote Attendance (Manager)

**Endpoint:** `<base_url>/api/method/client_demo.services.remote_attendance.reject_remote_attendance`  
**Method:** POST

### Input Parameters
```json
{
  "name": "RA-2026-00001",
  "manager": "VINOD K",
  "reason": "GPS location not matching work area"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | String | ✅ Yes | Remote Attendance ID |
| manager | String | ✅ Yes | Manager's Employee ID |
| reason | String | ✅ Yes | Rejection reason (mandatory) |

### Output Format
```json
{
  "message": {
    "success": true,
    "message": "Remote Attendance RA-2026-00001 rejected",
    "reason": "GPS location not matching work area"
  }
}
```

---

## 17. Get Approval History (Manager)

**Endpoint:** `<base_url>/api/method/client_demo.services.remote_attendance.get_approval_history`  
**Method:** POST

### Input Parameters
```json
{
  "user_id": "vinod@softlandindia.co.in",
  "from_date": "2026-01-01",
  "to_date": "2026-01-31"
}
```

### Output Format
```json
{
  "message": {
    "success": true,
    "manager": "VINOD K",
    "count": 10,
    "approved": 8,
    "rejected": 2,
    "data": [
      {
        "name": "RA-2026-00001",
        "employee": "AMAL R",
        "log_type": "IN",
        "workflow_state": "Approved",
        "approved_on": "2026-01-27 10:00:00"
      }
    ]
  }
}
```

---

# Error Response Format

```json
{
  "message": {
    "success": false,
    "message": "Error description"
  }
}
```

---

# Important Notes

1. **Base URL:** Replace `<base_url>` with your actual server URL
2. **Employee ID:** Always use the unique Employee name field (e.g., "AMAL R")
3. **Date Format:** All dates must be in YYYY-MM-DD format
4. **Location Type:** Required only for IN attendance (Work From Home / Field / Service Center)
5. **Content-Type:** Always set `Content-Type: application/json` header
6. **Method:** All endpoints use POST method

---

**Document Version:** 2.0  
**Total APIs:** 17  
**Last Updated:** January 27, 2026
