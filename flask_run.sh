#!/usr/bin/env sh

# Check if running inside Docker
if [ "${DOCKER}" = true ] ; then
  host="--host=0.0.0.0"
fi

if [ "${ENV}" = "dev" ] ; then
  debug="--debug"
fi

if [ -n "${PORT}" ] ; then
  port="-p ${PORT}"
fi

flask run ${host} ${debug} ${port}
