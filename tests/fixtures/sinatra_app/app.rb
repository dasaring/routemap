require 'sinatra'
require 'json'

# List all users
get '/users' do
  content_type :json
  { users: [] }.to_json
end

# Create a user
post '/users' do
  content_type :json
  { message: 'created' }.to_json
end

# Get a single user
get '/users/:id' do
  content_type :json
  { id: params[:id] }.to_json
end

# Update a user
put '/users/:id' do
  content_type :json
  { message: 'updated' }.to_json
end

# Partially update a user
patch '/users/:id' do
  content_type :json
  { message: 'patched' }.to_json
end

# Delete a user
delete '/users/:id' do
  content_type :json
  { message: 'deleted' }.to_json
end

get '/health' do
  'OK'
end
