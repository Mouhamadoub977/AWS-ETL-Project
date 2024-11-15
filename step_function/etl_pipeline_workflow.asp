{
  "StartAt": "Job1",
  "States": {
    "Job1": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "mo_job 1"
      },
      "Next": "Job2",
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "HandleFailure"
        }
      ]
    },
    "Job2": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "mo_job_2"
      },
      "Next": "Job3",
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "HandleFailure"
        }
      ]
    },
    "Job3": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "mo_job_3_OK"
      },
      "End": true,
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "HandleFailure"
        }
      ]
    },
    "HandleFailure": {
      "Type": "Fail",
      "Error": "JobFailed",
      "Cause": "Une des étapes du workflow a échoué"
    }
  }
}