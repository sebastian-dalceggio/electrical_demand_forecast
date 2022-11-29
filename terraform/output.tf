output "account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "airflow_web_server" {
  value = "${aws_instance.airflow.public_dns}:8080"
}

output "dashboard" {
  value = "${aws_instance.airflow.public_dns}:8501"
}

output "demand" {
  value = "${aws_ecr_repository.demand.repository_url}:${local.envs["DEMAND_DOCKER_IMAGE_TAG"]}"
  sensitive = true
}