package it.csi.proxy.ogcproxy.util;


import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jws;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.SignatureException;
import io.jsonwebtoken.UnsupportedJwtException;
import io.jsonwebtoken.impl.crypto.MacProvider;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

import java.time.Duration;
import java.time.Instant;
import java.time.temporal.TemporalAmount;
import java.util.Base64;
import java.util.Date;

public class JwtManager {

    private static final String CLAIM_USER = "user";

    private static final SignatureAlgorithm SIGNATURE_ALGORITHM = SignatureAlgorithm.HS256;
    //private static transient SecretKey SECRET_KEY = null;
    private static transient String ENCODED_KEY = "1Zc8EISmV2cHajvB3xpbgRRknfRl1LrmDvWCEnEZxQo=";
    private static final TemporalAmount TOKEN_VALIDITY = Duration.ofMinutes(30)/*Duration.ofHours( 4L )*/;

    public static SecretKey getSecretKey() {
    	if (ENCODED_KEY==null) {
    		SecretKey secretKey = MacProvider.generateKey( SIGNATURE_ALGORITHM );
            System.out.println("Inited SECRET_KEY: " + secretKey);
            // get base64 encoded version of the key
            ENCODED_KEY = Base64.getEncoder().encodeToString(secretKey.getEncoded());
            //System.out.println("SECRET_KEY: " + ENCODED_KEY);
        	return secretKey;
    	} else {
            System.out.println("Reusing SECRET_KEY: " + ENCODED_KEY);
            // decode the base64 encoded string
            byte[] decodedKey = Base64.getDecoder().decode(ENCODED_KEY);
            // rebuild key using SecretKeySpec
            SecretKey originalKey = new SecretKeySpec(decodedKey, 0, decodedKey.length, SIGNATURE_ALGORITHM.getValue());
        	return originalKey;
    	}
    }
    
    /**
     * Builds a JWT with the given subject and role and returns it as a JWS signed compact String.
     */
    public static String createToken( final String user, final String subject ) {
        final Instant now = Instant.now();
        final Date expiryDate = Date.from( now.plus( TOKEN_VALIDITY ) );
        return Jwts.builder()
                   .setSubject( subject )
                   .claim( CLAIM_USER, user )
                   .setExpiration( expiryDate )
                   .setIssuedAt( Date.from( now ) )
                   .signWith( SIGNATURE_ALGORITHM, getSecretKey() )
                   .compact();
    }

    /**
     * Parses the given JWS signed compact JWT, returning the claims.
     * If this method returns without throwing an exception, the token can be trusted.
     */
    public static Jws<Claims> parseToken( final String compactToken )
            throws ExpiredJwtException,
                   UnsupportedJwtException,
                   MalformedJwtException,
                   SignatureException,
                   IllegalArgumentException {
        return Jwts.parser()
                   .setSigningKey( getSecretKey() )
                   .parseClaimsJws( compactToken );
    }
}
