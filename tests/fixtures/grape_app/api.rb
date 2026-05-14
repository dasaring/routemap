require 'grape'

class UserAPI < Grape::API
  format :json

  namespace 'users' do
    get '/' do
      User.all
    end

    post '/' do
      User.create(params)
    end

    namespace ':id' do
      get '/' do
        User.find(params[:id])
      end

      put '/' do
        User.update(params[:id], params)
      end

      delete '/' do
        User.destroy(params[:id])
      end
    end
  end

  namespace 'health' do
    get '/check' do
      { status: 'ok' }
    end
  end
end
