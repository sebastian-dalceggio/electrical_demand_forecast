# resource "docker_image" "demand_image" {
#   name = local.envs["DEMAND_DOCKER_IMAGE"]
#   build {
#     dockerfile = "/Dockerfile"
#     path       = "../"
#   }
# }

resource "aws_ecr_repository" "demand" {
  name = local.envs["DEMAND_DOCKER_IMAGE_NAME"]
}

resource "docker_registry_image" "demand" {
  name = "${aws_ecr_repository.demand.repository_url}:${local.envs["DEMAND_DOCKER_IMAGE_TAG"]}"
  build {
    dockerfile = "/Dockerfile"
    context    = "../scripts"
  }
}

# resource "aws_ecr_repository" "database_api" {
#   name = local.envs["DATABASE_API_DOCKER_IMAGE_NAME"]
# }

# resource "docker_registry_image" "database_api" {
#   name = "${aws_ecr_repository.database_api.repository_url}:${local.envs["DATABASE_API_DOCKER_IMAGE_TAG"]}"
#   build {
#     dockerfile = "/Dockerfile_database_api"
#     context    = "../scripts"
#     build_args = {
#       BASE_IMAGE : "${aws_ecr_repository.demand.repository_url}:${local.envs["DEMAND_DOCKER_IMAGE_TAG"]}"
#     }
#   }
#   depends_on = [
#     docker_registry_image.demand
#   ]
# }

# resource "aws_ecr_repository" "dashboard" {
#   name = local.envs["DASHBOARD_DOCKER_IMAGE_NAME"]
# }

# resource "docker_registry_image" "dashboard" {
#   name = "${aws_ecr_repository.dashboard.repository_url}:${local.envs["DASHBOARD_DOCKER_IMAGE_TAG"]}"
#   build {
#     dockerfile = "/Dockerfile_dashboard"
#     context    = "../scripts"
#     build_args = {
#       BASE_IMAGE : "${aws_ecr_repository.demand.repository_url}:${local.envs["DEMAND_DOCKER_IMAGE_TAG"]}"
#     }
#   }
#   depends_on = [
#     docker_registry_image.demand
#   ]
# }