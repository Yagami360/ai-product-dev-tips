// Copyright 2017 Google
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#import <Foundation/Foundation.h>

#import "Functions/FirebaseFunctions/Public/FirebaseFunctions/FIRFunctions.h"

@protocol FIRAuthInterop;
@protocol FIRMessagingInterop;
@class FIRHTTPSCallableResult;

NS_ASSUME_NONNULL_BEGIN

@interface FIRFunctions (Internal)

/**
 * Calls an http trigger endpoint.
 * @param name The name of the http trigger.
 * @param data Parameters to pass to the function. Can be anything encodable as JSON.
 * @param completion The block to call when the request is complete.
 */
- (void)callFunction:(NSString *)name
          withObject:(nullable id)data
             timeout:(NSTimeInterval)timeout
          completion:(void (^)(FIRHTTPSCallableResult *_Nullable result,
                               NSError *_Nullable error))completion;

/**
 * Constructs the url for an http trigger. This is exposed only for testing.
 * @param name The name of the endpoint.
 */
- (NSString *)URLWithName:(NSString *)name;

/**
 * Sets the functions client to send requests to localhost instead of Firebase.
 * For testing only.
 */
- (void)useLocalhost;

/**
 * Internal initializer for the Cloud Functions client.
 * @param projectID The project ID for the Firebase project.
 * @param region The region for the http trigger, such as "us-central1".
 * @param customDomain A custom domain for the http trigger, such as "https://mydomain.com".
 * @param auth The auth provider to use (optional).
 * @param messaging The messaging interop to use (optional).
 */
- (id)initWithProjectID:(NSString *)projectID
                 region:(NSString *)region
           customDomain:(nullable NSString *)customDomain
                   auth:(nullable id<FIRAuthInterop>)auth
              messaging:(nullable id<FIRMessagingInterop>)messaging;

@end

NS_ASSUME_NONNULL_END
