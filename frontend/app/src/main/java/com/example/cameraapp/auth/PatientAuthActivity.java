package com.example.cameraapp.auth;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.cameraapp.MainActivity;
import com.example.cameraapp.R;

public class PatientAuthActivity extends AppCompatActivity {
    EditText email,pass,cpass;
    Button btn;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_patient_auth);
        email = findViewById(R.id.email);
        pass = findViewById(R.id.pass);
        cpass = findViewById(R.id.cpass);
        btn = findViewById(R.id.button);

        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(email.getText().toString().equals("") || pass.getText().toString().equals("") || cpass.getText().toString().equals("")){
                    Toast.makeText(PatientAuthActivity.this,"Enter your credentials!",Toast.LENGTH_LONG).show();
                    return;
                }
                String e = email.getText().toString();
                String p = pass.getText().toString();
                String c = cpass.getText().toString();
                if(!c.equals(p)){
                    Toast.makeText(PatientAuthActivity.this,"The passwords do not match!",Toast.LENGTH_LONG).show();
                    return;
                }
                Intent intent = new Intent(PatientAuthActivity.this,PatientDetailsActivity.class);
                intent.putExtra("email",e);
                intent.putExtra("password",p);
                startActivity(intent);
            }
        });
    }
}