Rails.application.routes.draw do
  get '/health', to: 'health#check', as: 'health'

  resources :users
  resources :posts

  get '/users/:id/profile', to: 'users#profile'
  post '/users/:id/avatar', to: 'users#upload_avatar'

  namespace :api do
    resources :products
    get '/stats', to: 'stats#index'
    delete '/cache', to: 'cache#clear'
  end

  patch '/settings', to: 'settings#update'
end
