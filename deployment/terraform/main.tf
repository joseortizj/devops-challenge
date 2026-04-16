provider "helm" {
  kubernetes = {
    config_path = "~/.kube/config"
  }
}

resource "helm_release" "postgres" {
  name       = "postgres"
  chart      = "./charts/postgres"
  set = [
    {
      name  = "service.type"
      value = "ClusterIP"
    }
  ]
}

resource "helm_release" "votes-api" {
  name       = "votes-api"
  chart      = "./charts/votes-api"
  set = [
    {
      name  = "service.type"
      value = "ClusterIP"
    }
  ]
}

resource "helm_release" "votes-ui" {
  name       = "votes-ui"
  chart      = "./charts/votes-ui"
  set = [
    {
      name  = "service.type"
      value = "ClusterIP"
    }
  ]
}

resource "helm_release" "nginx" {
  name       = "nginx"
  chart      = "./charts/nginx"
  set = [
    {
      name  = "service.type"
      value = "ClusterIP"
    }
  ]
}