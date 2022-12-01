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